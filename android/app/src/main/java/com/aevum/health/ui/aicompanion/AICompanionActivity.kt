package com.aevum.health.ui.aicompanion

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.aevum.health.R
import com.aevum.health.databinding.ActivityAicompanionBinding
import com.aevum.health.network.RetrofitClient
import com.aevum.health.repository.AuthRepository
import kotlinx.coroutines.launch

data class ChatMessage(val sender: String, val text: String)

class AICompanionActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityAicompanionBinding
    private lateinit var authRepository: AuthRepository
    private lateinit var messagesAdapter: MessagesAdapter
    private val messages = mutableListOf<ChatMessage>()
    private var threadId: String? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityAicompanionBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // Enable back button
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "AI Companion"
        
        authRepository = AuthRepository(this)
        
        setupRecyclerView()
        setupClickListeners()
        
        // Add welcome message
        messages.add(ChatMessage("ai", "Hi! I am your AI Companion. How can I help you today?"))
        messagesAdapter.notifyDataSetChanged()
    }
    
    private fun setupRecyclerView() {
        messagesAdapter = MessagesAdapter(messages)
        binding.rvMessages.layoutManager = LinearLayoutManager(this)
        binding.rvMessages.adapter = messagesAdapter
    }
    
    private fun setupClickListeners() {
        binding.btnSend.setOnClickListener {
            sendMessage()
        }
    }
    
    private fun sendMessage() {
        val messageText = binding.etMessage.text.toString().trim()
        if (messageText.isEmpty()) return
        
        // Disable input while sending
        binding.btnSend.isEnabled = false
        binding.etMessage.isEnabled = false
        binding.etMessage.text?.clear()
        
        // Add loading indicator
        val loadingMessageIndex = messages.size
        messages.add(ChatMessage("ai", "Thinking..."))
        messagesAdapter.notifyItemInserted(loadingMessageIndex)
        binding.rvMessages.smoothScrollToPosition(loadingMessageIndex)
        
        // Send to API
        lifecycleScope.launch {
            try {
                val token = authRepository.getAccessToken()
                if (token == null) {
                    // Remove loading message
                    messages.removeAt(loadingMessageIndex)
                    messagesAdapter.notifyItemRemoved(loadingMessageIndex)
                    messages.add(ChatMessage("ai", "Please login to use AI Companion"))
                    messagesAdapter.notifyItemInserted(messages.size - 1)
                    binding.rvMessages.smoothScrollToPosition(messages.size - 1)
                    binding.btnSend.isEnabled = true
                    binding.etMessage.isEnabled = true
                    return@launch
                }
                
                val apiService = RetrofitClient.createApiServiceWithToken(token)
                
                // Create thread if needed
                if (threadId == null) {
                    val threadTitle = messageText.take(50).ifEmpty { "New Chat" }
                    val createThreadRequest = com.aevum.health.data.models.CreateThreadRequest(
                        title = threadTitle,
                        category = "MENTAL_HEALTH"
                    )
                    
                    android.util.Log.d("AICompanion", "Creating thread with title: $threadTitle, token: ${token.take(20)}...")
                    val threadResponse = apiService.createThread(createThreadRequest)
                    
                    android.util.Log.d("AICompanion", "Thread creation response: code=${threadResponse.code()}, isSuccessful=${threadResponse.isSuccessful}")
                    
                    if (threadResponse.isSuccessful) {
                        val responseBody = threadResponse.body()
                        if (responseBody != null) {
                            val responseThreadId = responseBody.threadId
                            if (responseThreadId != null) {
                                threadId = responseThreadId
                                android.util.Log.d("AICompanion", "Thread created successfully: $threadId")
                            } else {
                                android.util.Log.e("AICompanion", "Thread ID is null in response")
                                // Try to log the raw response
                                android.util.Log.e("AICompanion", "Response body: $responseBody")
                                // Remove loading message
                                messages.removeAt(loadingMessageIndex)
                                messagesAdapter.notifyItemRemoved(loadingMessageIndex)
                                messages.add(ChatMessage("ai", "Failed to create thread: thread_id is missing in response"))
                                messagesAdapter.notifyItemInserted(messages.size - 1)
                                binding.rvMessages.smoothScrollToPosition(messages.size - 1)
                                binding.btnSend.isEnabled = true
                                binding.etMessage.isEnabled = true
                                return@launch
                            }
                        } else {
                            android.util.Log.e("AICompanion", "Thread response body is null")
                            // Remove loading message
                            messages.removeAt(loadingMessageIndex)
                            messagesAdapter.notifyItemRemoved(loadingMessageIndex)
                            messages.add(ChatMessage("ai", "Failed to create chat thread: Response body is null"))
                            messagesAdapter.notifyItemInserted(messages.size - 1)
                            binding.rvMessages.smoothScrollToPosition(messages.size - 1)
                            binding.btnSend.isEnabled = true
                            binding.etMessage.isEnabled = true
                            return@launch
                        }
                    } else {
                        // Remove loading message
                        messages.removeAt(loadingMessageIndex)
                        messagesAdapter.notifyItemRemoved(loadingMessageIndex)
                        
                        // Log error for debugging
                        val errorBody = try {
                            threadResponse.errorBody()?.string() ?: "Unknown error"
                        } catch (e: Exception) {
                            "Error reading error body: ${e.message}"
                        }
                        val errorMessage = "Failed to create chat thread: ${threadResponse.code()} - $errorBody"
                        android.util.Log.e("AICompanion", errorMessage)
                        
                        messages.add(ChatMessage("ai", "Failed to create chat thread. Please try again. (Error: ${threadResponse.code()})"))
                        messagesAdapter.notifyItemInserted(messages.size - 1)
                        binding.rvMessages.smoothScrollToPosition(messages.size - 1)
                        binding.btnSend.isEnabled = true
                        binding.etMessage.isEnabled = true
                        return@launch
                    }
                }
                
                // Send message to chat endpoint
                val chatRequest = com.aevum.health.data.models.ChatMessageRequest(
                    threadId = threadId!!,
                    message = messageText,
                    workflowType = "MENTAL_HEALTH"
                )
                android.util.Log.d("AICompanion", "Sending chat message to thread: $threadId")
                val chatResponse = apiService.sendChatMessage(chatRequest)
                
                // Remove loading message
                messages.removeAt(loadingMessageIndex)
                messagesAdapter.notifyItemRemoved(loadingMessageIndex)
                
                if (chatResponse.isSuccessful && chatResponse.body() != null) {
                    val response = chatResponse.body()!!
                    // Add both user and AI messages from response (matching React behavior)
                    messages.add(ChatMessage("user", response.userMessage.content))
                    messages.add(ChatMessage("ai", response.aiResponse.content))
                    messagesAdapter.notifyItemRangeInserted(messages.size - 2, 2)
                    binding.rvMessages.smoothScrollToPosition(messages.size - 1)
                } else {
                    val errorBody = chatResponse.errorBody()?.string() ?: "Unknown error"
                    messages.add(ChatMessage("ai", "Sorry, something went wrong. Please try again. ($errorBody)"))
                    messagesAdapter.notifyItemInserted(messages.size - 1)
                    binding.rvMessages.smoothScrollToPosition(messages.size - 1)
                }
            } catch (e: Exception) {
                // Remove loading message
                if (messages.size > loadingMessageIndex && messages[loadingMessageIndex].text == "Thinking...") {
                    messages.removeAt(loadingMessageIndex)
                    messagesAdapter.notifyItemRemoved(loadingMessageIndex)
                }
                messages.add(ChatMessage("ai", "Sorry, something went wrong: ${e.message}"))
                messagesAdapter.notifyItemInserted(messages.size - 1)
                binding.rvMessages.smoothScrollToPosition(messages.size - 1)
            } finally {
                // Re-enable input
                binding.btnSend.isEnabled = true
                binding.etMessage.isEnabled = true
            }
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        onBackPressedDispatcher.onBackPressed()
        return true
    }
}

class MessagesAdapter(private val messages: List<ChatMessage>) : RecyclerView.Adapter<MessagesAdapter.MessageViewHolder>() {
    
    class MessageViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvMessage: TextView = itemView.findViewById(R.id.tvMessage)
    }
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MessageViewHolder {
        val layoutId = if (viewType == 0) R.layout.item_message_user else R.layout.item_message_ai
        val view = LayoutInflater.from(parent.context).inflate(layoutId, parent, false)
        return MessageViewHolder(view)
    }
    
    override fun onBindViewHolder(holder: MessageViewHolder, position: Int) {
        holder.tvMessage.text = messages[position].text
    }
    
    override fun getItemCount() = messages.size
    
    override fun getItemViewType(position: Int) = if (messages[position].sender == "user") 0 else 1
}

