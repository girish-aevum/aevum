package com.aevum.health.ui.subscription

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.aevum.health.R
import com.aevum.health.data.models.SubscriptionData
import com.aevum.health.data.models.SubscriptionPlan
import com.aevum.health.databinding.ActivitySubscriptionBinding
import com.aevum.health.databinding.ItemPlanFeatureBinding
import com.aevum.health.databinding.ItemSubscriptionPlanBinding
import com.aevum.health.network.RetrofitClient
import com.aevum.health.repository.AuthRepository
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class SubscriptionActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivitySubscriptionBinding
    private lateinit var authRepository: AuthRepository
    private lateinit var plansAdapter: SubscriptionPlansAdapter
    private var subscriptionPlans: List<SubscriptionPlan> = emptyList()
    private var currentSubscription: SubscriptionData? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySubscriptionBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Subscription"
        
        authRepository = AuthRepository(this)
        
        setupRecyclerView()
        loadSubscriptionData()
    }
    
    private fun setupRecyclerView() {
        plansAdapter = SubscriptionPlansAdapter(subscriptionPlans, currentSubscription) { plan ->
            handlePlanSelect(plan)
        }
        binding.rvSubscriptionPlans.layoutManager = LinearLayoutManager(this, LinearLayoutManager.HORIZONTAL, false)
        binding.rvSubscriptionPlans.adapter = plansAdapter
    }
    
    private fun loadSubscriptionData() {
        lifecycleScope.launch {
            try {
                val token = authRepository.getAccessToken()
                if (token == null) {
                    showError("Please login to view subscription plans")
                    return@launch
                }
                
                val apiService = RetrofitClient.createApiServiceWithToken(token)
                
                // Fetch subscription plans
                val plansResponse = apiService.getSubscriptionPlans()
                if (plansResponse.isSuccessful && plansResponse.body() != null) {
                    val paginatedResponse = plansResponse.body()!!
                    subscriptionPlans = paginatedResponse.results ?: emptyList()
                    android.util.Log.d("Subscription", "Loaded ${subscriptionPlans.size} subscription plans")
                } else {
                    android.util.Log.e("Subscription", "Failed to load plans: ${plansResponse.code()}")
                }
                
                // Fetch current subscription
                val subscriptionResponse = apiService.getMySubscription()
                if (subscriptionResponse.isSuccessful && subscriptionResponse.body() != null) {
                    currentSubscription = subscriptionResponse.body()
                    updateCurrentSubscriptionDisplay()
                }
                
                // Update adapter
                plansAdapter.updateData(subscriptionPlans, currentSubscription)
                
            } catch (e: Exception) {
                android.util.Log.e("Subscription", "Failed to load subscription data: ${e.message}", e)
                showError("Failed to load subscription information: ${e.message}")
            }
        }
    }
    
    private fun updateCurrentSubscriptionDisplay() {
        val subscription = currentSubscription
        if (subscription != null && subscription.plan != null) {
            binding.cardCurrentSubscription.visibility = View.VISIBLE
            binding.tvCurrentPlanName.text = subscription.plan.name ?: "N/A"
            
            val endDate = subscription.endDate?.let { formatDate(it) } ?: "N/A"
            binding.tvCurrentPlanRenewal.text = "Renews on $endDate"
        } else {
            binding.cardCurrentSubscription.visibility = View.GONE
        }
    }
    
    private fun formatDate(dateString: String): String {
        return try {
            val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
            val outputFormat = SimpleDateFormat("MMM dd, yyyy", Locale.getDefault())
            val date = inputFormat.parse(dateString)
            date?.let { outputFormat.format(it) } ?: dateString
        } catch (e: Exception) {
            dateString
        }
    }
    
    private fun handlePlanSelect(plan: SubscriptionPlan) {
        val isCurrentPlan = currentSubscription?.plan?.id == plan.id
        if (isCurrentPlan) {
            Toast.makeText(this, "This is your current plan", Toast.LENGTH_SHORT).show()
            return
        }
        
        val action = if (currentSubscription != null) "upgrade to" else "select"
        val actionTitle = action.replaceFirstChar { it.uppercase() }
        AlertDialog.Builder(this)
            .setTitle("Confirm $actionTitle")
            .setMessage("Are you sure you want to $action the ${plan.name} plan?")
            .setPositiveButton("Yes") { _, _ ->
                // TODO: Implement subscription upgrade/selection
                Toast.makeText(this, "Subscription ${action} feature coming soon", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
    
    private fun showError(message: String) {
        binding.tvError.text = message
        binding.tvError.visibility = View.VISIBLE
    }
    
    override fun onSupportNavigateUp(): Boolean {
        onBackPressedDispatcher.onBackPressed()
        return true
    }
}

class SubscriptionPlansAdapter(
    private var plans: List<SubscriptionPlan>,
    private var currentSubscription: SubscriptionData?,
    private val onPlanSelect: (SubscriptionPlan) -> Unit
) : RecyclerView.Adapter<SubscriptionPlansAdapter.PlanViewHolder>() {
    
    fun updateData(newPlans: List<SubscriptionPlan>, newSubscription: SubscriptionData?) {
        plans = newPlans
        currentSubscription = newSubscription
        notifyDataSetChanged()
    }
    
    class PlanViewHolder(val binding: ItemSubscriptionPlanBinding) : RecyclerView.ViewHolder(binding.root)
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): PlanViewHolder {
        val binding = ItemSubscriptionPlanBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return PlanViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: PlanViewHolder, position: Int) {
        val plan = plans[position]
        val isCurrentPlan = currentSubscription?.plan?.id == plan.id
        
        holder.binding.tvPlanName.text = plan.name ?: "N/A"
        holder.binding.tvPlanPrice.text = "₹${plan.price ?: "0"}"
        holder.binding.tvBillingCycle.text = "/ ${plan.billingCycle ?: "Monthly"}"
        holder.binding.tvPlanDescription.text = plan.description ?: ""
        
        // Show/hide current plan badge
        holder.binding.tvCurrentPlanBadge.visibility = if (isCurrentPlan) View.VISIBLE else View.GONE
        
        // Parse and display features
        val features = parseFeatures(plan.features)
        val featuresAdapter = PlanFeaturesAdapter(features)
        holder.binding.rvPlanFeatures.layoutManager = LinearLayoutManager(holder.itemView.context)
        holder.binding.rvPlanFeatures.adapter = featuresAdapter
        
        // Set button text
        holder.binding.btnSelectPlan.text = if (isCurrentPlan) {
            "Current Plan"
        } else if (currentSubscription != null) {
            "Upgrade"
        } else {
            "Select Plan"
        }
        
        holder.binding.btnSelectPlan.isEnabled = !isCurrentPlan
        
        holder.binding.btnSelectPlan.setOnClickListener {
            if (!isCurrentPlan) {
                onPlanSelect(plan)
            }
        }
    }
    
    override fun getItemCount() = plans.size
    
    private fun parseFeatures(features: Any?): List<String> {
        if (features == null) return emptyList()
        
        return when (features) {
            is List<*> -> features.mapNotNull { it?.toString() }
            is String -> features.split(",").map { it.trim() }.filter { it.isNotEmpty() }
            else -> listOf(features.toString())
        }
    }
}

class PlanFeaturesAdapter(private val features: List<String>) : RecyclerView.Adapter<PlanFeaturesAdapter.FeatureViewHolder>() {
    
    class FeatureViewHolder(val binding: ItemPlanFeatureBinding) : RecyclerView.ViewHolder(binding.root)
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): FeatureViewHolder {
        val binding = ItemPlanFeatureBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return FeatureViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: FeatureViewHolder, position: Int) {
        holder.binding.tvFeature.text = features[position]
    }
    
    override fun getItemCount() = features.size
}
