package com.aevum.health.ui.dashboard

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GravityCompat
import androidx.drawerlayout.widget.DrawerLayout
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.aevum.health.R
import com.aevum.health.data.models.DNAOrder
import com.aevum.health.data.models.SubscriptionData
import com.aevum.health.databinding.ActivityDashboardBinding
import com.aevum.health.databinding.ItemDashboardCardBinding
import com.aevum.health.databinding.ItemDnaOrderBinding
import com.aevum.health.network.RetrofitClient
import com.aevum.health.repository.AuthRepository
import com.aevum.health.ui.auth.LoginActivity
import com.aevum.health.ui.profile.ProfileActivity
import com.aevum.health.ui.settings.SettingsActivity
import com.aevum.health.ui.mentalwellness.MentalWellnessActivity
import com.aevum.health.ui.nutrition.NutritionActivity
import com.aevum.health.ui.aicompanion.AICompanionActivity
import com.aevum.health.ui.aicompanionraw.AICompanionRawActivity
import com.aevum.health.ui.dnaprofiling.DNAProfilingActivity
import com.aevum.health.ui.smartjournal.SmartJournalActivity
import com.aevum.health.ui.changepassword.ChangePasswordActivity
import com.aevum.health.ui.subscription.SubscriptionActivity
import com.google.android.material.navigation.NavigationView
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class DashboardActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityDashboardBinding
    private lateinit var authRepository: AuthRepository
    private lateinit var dashboardAdapter: DashboardAdapter
    private var dnaOrders: List<DNAOrder> = emptyList()
    private var subscriptionData: SubscriptionData? = null
    private var currentUser: com.aevum.health.data.models.User? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityDashboardBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        supportActionBar?.title = "Dashboard"
        supportActionBar?.setDisplayHomeAsUpEnabled(false)
        
        authRepository = AuthRepository(this)
        
        setupDashboard()
        setupClickListeners()
        loadUserProfile()
        loadDashboardData()
    }
    
    private fun setupDashboard() {
        dashboardAdapter = DashboardAdapter(emptyList(), dnaOrders, subscriptionData) { cardType ->
            handleCardClick(cardType)
        }
        binding.rvDashboardCards.layoutManager = LinearLayoutManager(this)
        binding.rvDashboardCards.adapter = dashboardAdapter
        
        // Create initial cards
        updateDashboardCards()
    }
    
    private fun setupClickListeners() {
        binding.btnMenu.setOnClickListener {
            binding.drawerLayout.openDrawer(GravityCompat.START)
        }
        
        binding.navView.setNavigationItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_dashboard -> {
                    binding.drawerLayout.closeDrawer(GravityCompat.START)
                    true
                }
                R.id.nav_smart_journal -> {
                    binding.drawerLayout.closeDrawer(GravityCompat.START)
                    startActivity(Intent(this, SmartJournalActivity::class.java))
                    true
                }
                R.id.nav_mental_wellness -> {
                    binding.drawerLayout.closeDrawer(GravityCompat.START)
                    startActivity(Intent(this, MentalWellnessActivity::class.java))
                    true
                }
                R.id.nav_nutrition -> {
                    binding.drawerLayout.closeDrawer(GravityCompat.START)
                    startActivity(Intent(this, NutritionActivity::class.java))
                    true
                }
                R.id.nav_ai_companion -> {
                    binding.drawerLayout.closeDrawer(GravityCompat.START)
                    startActivity(Intent(this, AICompanionActivity::class.java))
                    true
                }
                R.id.nav_ai_companion_raw -> {
                    binding.drawerLayout.closeDrawer(GravityCompat.START)
                    startActivity(Intent(this, AICompanionRawActivity::class.java))
                    true
                }
                R.id.nav_dna_profiling -> {
                    binding.drawerLayout.closeDrawer(GravityCompat.START)
                    startActivity(Intent(this, DNAProfilingActivity::class.java))
                    true
                }
                R.id.nav_profile -> {
                    binding.drawerLayout.closeDrawer(GravityCompat.START)
                    startActivity(Intent(this, ProfileActivity::class.java))
                    true
                }
                R.id.nav_settings -> {
                    binding.drawerLayout.closeDrawer(GravityCompat.START)
                    startActivity(Intent(this, SettingsActivity::class.java))
                    true
                }
                R.id.nav_change_password -> {
                    binding.drawerLayout.closeDrawer(GravityCompat.START)
                    startActivity(Intent(this, ChangePasswordActivity::class.java))
                    true
                }
                R.id.nav_subscription -> {
                    binding.drawerLayout.closeDrawer(GravityCompat.START)
                    startActivity(Intent(this, SubscriptionActivity::class.java))
                    true
                }
                R.id.nav_logout -> {
                    binding.drawerLayout.closeDrawer(GravityCompat.START)
                    performLogout()
                    true
                }
                else -> false
            }
        }
    }
    
    private fun loadUserProfile() {
        lifecycleScope.launch {
            val result = authRepository.getProfile()
            result.onSuccess { profile ->
                val user = profile.user
                if (user != null) {
                    val fullName = user.fullName?.takeIf { it.isNotBlank() } ?: buildString {
                        if (!user.firstName.isNullOrBlank()) {
                            append(user.firstName)
                        }
                        if (!user.lastName.isNullOrBlank()) {
                            if (isNotEmpty()) append(" ")
                            append(user.lastName)
                        }
                        if (isEmpty()) {
                            append(user.username ?: user.email?.split("@")?.get(0) ?: "User")
                        }
                    }.trim()
                    
                    binding.tvWelcome.text = "Welcome, $fullName!"
                    binding.tvEmail.text = user.email ?: "N/A"
                    
                    val headerView = binding.navView.getHeaderView(0)
                    val navUserName = headerView.findViewById<TextView>(R.id.tvNavUserName)
                    val navUserEmail = headerView.findViewById<TextView>(R.id.tvNavUserEmail)
                    
                    navUserName?.text = fullName
                    navUserEmail?.text = user.email ?: "N/A"
                    
                    // Store user for card updates
                    currentUser = user
                    updateDashboardCards()
                }
            }.onFailure { exception ->
                android.util.Log.e("Dashboard", "Failed to load profile: ${exception.message}", exception)
            }
        }
    }
    
    private fun loadDashboardData() {
        lifecycleScope.launch {
            try {
                val token = authRepository.getAccessToken()
                if (token == null) return@launch
                
                val apiService = RetrofitClient.createApiServiceWithToken(token)
                
                // Fetch DNA orders
                val dnaResponse = apiService.getDNAOrders()
                if (dnaResponse.isSuccessful && dnaResponse.body() != null) {
                    dnaOrders = dnaResponse.body()!!.results ?: emptyList()
                    android.util.Log.d("Dashboard", "Loaded ${dnaOrders.size} DNA orders")
                }
                
                // Fetch subscription
                val subscriptionResponse = apiService.getMySubscription()
                if (subscriptionResponse.isSuccessful && subscriptionResponse.body() != null) {
                    subscriptionData = subscriptionResponse.body()
                    android.util.Log.d("Dashboard", "Loaded subscription: ${subscriptionData?.plan?.name}")
                }
                
                // Refresh cards with updated data (this will use the latest dnaOrders and subscriptionData)
                updateDashboardCards()
                
            } catch (e: Exception) {
                android.util.Log.e("Dashboard", "Failed to load dashboard data: ${e.message}", e)
            }
        }
    }
    
    private fun updateDashboardCards() {
        val cards = createDashboardCards()
        dashboardAdapter.updateCards(cards)
    }
    
    private fun createDashboardCards(): List<DashboardCard> {
        val user = currentUser
        val fullName = user?.fullName?.takeIf { it.isNotBlank() } ?: buildString {
            if (!user?.firstName.isNullOrBlank()) append(user?.firstName)
            if (!user?.lastName.isNullOrBlank()) {
                if (isNotEmpty()) append(" ")
                append(user?.lastName)
            }
            if (isEmpty()) append(user?.username ?: "User")
        }.trim()
        
        return listOf(
            DashboardCard(
                type = CardType.PROFILE,
                title = "Profile",
                icon = "👤",
                description = "Name: $fullName\nEmail: ${user?.email ?: "N/A"}",
                actionButtonText = "View Full Profile",
                action = { startActivity(Intent(this, ProfileActivity::class.java)) }
            ),
            DashboardCard(
                type = CardType.HEALTH_METRICS,
                title = "Health Metrics",
                icon = "❤️",
                description = "Track your health progress and metrics",
                actionButtonText = "View Details",
                action = { Toast.makeText(this, "Health Metrics - Coming soon", Toast.LENGTH_SHORT).show() }
            ),
            DashboardCard(
                type = CardType.SUBSCRIPTION,
                title = "Subscription",
                icon = "🛡️",
                description = subscriptionData?.let {
                    "Current Plan: ${it.plan?.name ?: "N/A"}\n" +
                    "Expiry Date: ${formatDate(it.endDate)}\n" +
                    "Status: ${it.status ?: "N/A"}"
                } ?: "No active subscription found",
                actionButtonText = if (subscriptionData != null) "Manage Subscription" else "View Plans",
                action = { startActivity(Intent(this, SubscriptionActivity::class.java)) }
            ),
            DashboardCard(
                type = CardType.DNA_PROFILING,
                title = "DNA Profiling",
                icon = "🧬",
                description = "Unlock personalized health insights through genetic testing.",
                actionButtonText = if (dnaOrders.isNotEmpty()) "View All Orders" else "Order DNA Kit",
                action = { startActivity(Intent(this, DNAProfilingActivity::class.java)) },
                dnaOrders = dnaOrders.take(2)
            ),
            DashboardCard(
                type = CardType.SMART_JOURNAL,
                title = "Smart Journal",
                icon = "📊",
                description = "Track your health, habits, and progress with the Smart Journal.",
                actionButtonText = "Go to Smart Journal",
                action = { startActivity(Intent(this, SmartJournalActivity::class.java)) }
            ),
            DashboardCard(
                type = CardType.MENTAL_WELLNESS,
                title = "Mental Wellness",
                icon = "🧠",
                description = "Tools and insights for your mental wellbeing.",
                actionButtonText = "Go to Mental Wellness",
                action = { startActivity(Intent(this, MentalWellnessActivity::class.java)) }
            ),
            DashboardCard(
                type = CardType.NUTRITION,
                title = "Nutrition",
                icon = "🍎",
                description = "Personalized nutrition tracking and advice.",
                actionButtonText = "Go to Nutrition",
                action = { startActivity(Intent(this, NutritionActivity::class.java)) }
            ),
            DashboardCard(
                type = CardType.AI_COMPANION,
                title = "AI Companion",
                icon = "✨",
                description = "Your personal AI assistant for health, wellness, and more.",
                actionButtonText = "Go to AI Companion",
                action = { startActivity(Intent(this, AICompanionActivity::class.java)) }
            )
        )
    }
    
    private fun formatDate(dateString: String?): String {
        if (dateString.isNullOrBlank()) return "N/A"
        return try {
            val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
            val outputFormat = SimpleDateFormat("MMM dd, yyyy", Locale.getDefault())
            val date = inputFormat.parse(dateString)
            date?.let { outputFormat.format(it) } ?: dateString
        } catch (e: Exception) {
            dateString
        }
    }
    
    private fun handleCardClick(cardType: CardType) {
        when (cardType) {
            CardType.PROFILE -> startActivity(Intent(this, ProfileActivity::class.java))
            CardType.HEALTH_METRICS -> Toast.makeText(this, "Health Metrics - Coming soon", Toast.LENGTH_SHORT).show()
            CardType.SUBSCRIPTION -> startActivity(Intent(this, SubscriptionActivity::class.java))
            CardType.DNA_PROFILING -> startActivity(Intent(this, DNAProfilingActivity::class.java))
            CardType.SMART_JOURNAL -> startActivity(Intent(this, SmartJournalActivity::class.java))
            CardType.MENTAL_WELLNESS -> startActivity(Intent(this, MentalWellnessActivity::class.java))
            CardType.NUTRITION -> startActivity(Intent(this, NutritionActivity::class.java))
            CardType.AI_COMPANION -> startActivity(Intent(this, AICompanionActivity::class.java))
        }
    }
    
    private fun performLogout() {
        lifecycleScope.launch {
            val result = authRepository.logout()
            result.onSuccess {
                Toast.makeText(this@DashboardActivity, "Logged out successfully", Toast.LENGTH_SHORT).show()
                startActivity(Intent(this@DashboardActivity, LoginActivity::class.java))
                finish()
            }.onFailure { exception ->
                Toast.makeText(this@DashboardActivity, "Logout failed: ${exception.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
}

enum class CardType {
    PROFILE, HEALTH_METRICS, SUBSCRIPTION, DNA_PROFILING, SMART_JOURNAL, MENTAL_WELLNESS, NUTRITION, AI_COMPANION
}

data class DashboardCard(
    val type: CardType,
    val title: String,
    val icon: String,
    val description: String,
    val actionButtonText: String,
    val action: () -> Unit,
    val dnaOrders: List<DNAOrder> = emptyList()
)

class DashboardAdapter(
    private var cards: List<DashboardCard>,
    private var dnaOrders: List<DNAOrder>,
    private var subscriptionData: SubscriptionData?,
    private val onCardClick: (CardType) -> Unit
) : RecyclerView.Adapter<DashboardAdapter.CardViewHolder>() {
    
    fun updateCards(newCards: List<DashboardCard>) {
        cards = newCards
        notifyDataSetChanged()
    }
    
    fun updateData(newDNAOrders: List<DNAOrder>, newSubscriptionData: SubscriptionData?) {
        dnaOrders = newDNAOrders
        subscriptionData = newSubscriptionData
        // Don't notify here - cards will be updated separately
    }
    
    class CardViewHolder(val binding: ItemDashboardCardBinding) : RecyclerView.ViewHolder(binding.root)
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CardViewHolder {
        val binding = ItemDashboardCardBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return CardViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: CardViewHolder, position: Int) {
        val card = cards[position]
        
        holder.binding.tvCardIcon.text = card.icon
        holder.binding.tvCardTitle.text = card.title
        holder.binding.tvCardDescription.text = card.description
        holder.binding.btnCardAction.text = card.actionButtonText
        
        holder.binding.btnCardAction.setOnClickListener {
            card.action()
        }
        
        // Handle DNA Orders display
        if (card.type == CardType.DNA_PROFILING && card.dnaOrders.isNotEmpty()) {
            holder.binding.rvDNAOrders.visibility = View.VISIBLE
            holder.binding.rvDNAOrders.layoutManager = LinearLayoutManager(holder.itemView.context)
            holder.binding.rvDNAOrders.adapter = DNAOrdersAdapter(card.dnaOrders)
        } else {
            holder.binding.rvDNAOrders.visibility = View.GONE
        }
    }
    
    override fun getItemCount() = cards.size
}

class DNAOrdersAdapter(private val orders: List<DNAOrder>) : RecyclerView.Adapter<DNAOrdersAdapter.OrderViewHolder>() {
    
    class OrderViewHolder(val binding: ItemDnaOrderBinding) : RecyclerView.ViewHolder(binding.root)
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): OrderViewHolder {
        val binding = ItemDnaOrderBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return OrderViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: OrderViewHolder, position: Int) {
        val order = orders[position]
        
        holder.binding.tvKitTypeName.text = order.kitTypeName ?: "DNA Kit"
        holder.binding.tvOrderId.text = "Order ID: ${order.orderId ?: "N/A"}"
        
        // Format order date
        val orderDate = order.orderDate?.let { formatOrderDate(it) } ?: "N/A"
        holder.binding.tvOrderDate.text = "Ordered on: $orderDate"
        
        // Set status badge
        val status = order.status ?: "PENDING"
        holder.binding.tvOrderStatus.text = status
        
        // Set status background color
        val statusBg = when (status.uppercase()) {
            "COMPLETED", "RESULTS_GENERATED" -> R.drawable.bg_status_completed
            "PROCESSING", "SAMPLE_RECEIVED" -> R.drawable.bg_status_processing
            else -> R.drawable.bg_status_pending
        }
        holder.binding.tvOrderStatus.setBackgroundResource(statusBg)
    }
    
    override fun getItemCount() = orders.size
    
    private fun formatOrderDate(dateString: String): String {
        return try {
            val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
            val outputFormat = SimpleDateFormat("MMM dd, yyyy", Locale.getDefault())
            val date = inputFormat.parse(dateString)
            date?.let { outputFormat.format(it) } ?: dateString
        } catch (e: Exception) {
            dateString
        }
    }
}
