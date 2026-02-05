package com.aevum.health.ui.aicompanionraw

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
import com.aevum.health.databinding.ActivityAicompanionrawBinding
import com.aevum.health.network.RetrofitClient
import com.aevum.health.repository.AuthRepository
import kotlinx.coroutines.launch

data class ChatMessage(val sender: String, val text: String)

class AICompanionRawActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityAicompanionrawBinding
    private lateinit var authRepository: AuthRepository
    private lateinit var messagesAdapter: MessagesAdapter
    private val messages = mutableListOf<ChatMessage>()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityAicompanionrawBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // Enable back button
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "AI Companion Raw"
        
        authRepository = AuthRepository(this)
        
        setupRecyclerView()
        setupClickListeners()
        
        // Add welcome message
        messages.add(ChatMessage("ai", "Hi! I am your Raw AI Companion. Ask me anything without summarization."))
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
                    messages.add(ChatMessage("ai", "Please login to use AI Companion Raw"))
                    messagesAdapter.notifyItemInserted(messages.size - 1)
                    binding.rvMessages.smoothScrollToPosition(messages.size - 1)
                    binding.btnSend.isEnabled = true
                    binding.etMessage.isEnabled = true
                    return@launch
                }
                
                val apiService = RetrofitClient.createApiServiceWithToken(token)
                
                // Send message to raw AI companion endpoint
                val request = mapOf("text" to messageText)
                android.util.Log.d("AICompanionRaw", "Sending message to raw endpoint: $messageText")
                val response = apiService.sendRawMessage(request)
                
                // Remove loading message
                messages.removeAt(loadingMessageIndex)
                messagesAdapter.notifyItemRemoved(loadingMessageIndex)
                
                if (response.isSuccessful && response.body() != null) {
                    val responseBody = response.body()!!
                    // Add both user and AI messages
                    messages.add(ChatMessage("user", messageText))
                    messages.add(ChatMessage("ai", responseBody.text))
                    messagesAdapter.notifyItemRangeInserted(messages.size - 2, 2)
                    binding.rvMessages.smoothScrollToPosition(messages.size - 1)
                } else {
                    val errorBody = response.errorBody()?.string() ?: "Unknown error"
                    android.util.Log.e("AICompanionRaw", "Error response: ${response.code()} - $errorBody")
                    messages.add(ChatMessage("ai", "Sorry, something went wrong. Please try again."))
                    messagesAdapter.notifyItemInserted(messages.size - 1)
                    binding.rvMessages.smoothScrollToPosition(messages.size - 1)
                }
            } catch (e: Exception) {
                // Remove loading message
                if (messages.size > loadingMessageIndex && messages[loadingMessageIndex].text == "Thinking...") {
                    messages.removeAt(loadingMessageIndex)
                    messagesAdapter.notifyItemRemoved(loadingMessageIndex)
                }
                android.util.Log.e("AICompanionRaw", "Exception: ${e.message}", e)
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

