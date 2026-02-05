package com.aevum.health.ui.dnaprofiling

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.aevum.health.R
import com.aevum.health.data.models.DNAKitType
import com.aevum.health.data.models.DNAOrder
import com.aevum.health.data.models.DNAReport
import com.aevum.health.databinding.ActivityDnaprofilingBinding
import com.aevum.health.databinding.ItemDnaKitBinding
import com.aevum.health.databinding.ItemDnaOrderDetailBinding
import com.aevum.health.databinding.ItemKeyFindingBinding
import com.aevum.health.databinding.ItemPlanFeatureBinding
import com.aevum.health.network.RetrofitClient
import com.aevum.health.repository.AuthRepository
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

class DNAProfilingActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityDnaprofilingBinding
    private lateinit var authRepository: AuthRepository
    private lateinit var dnaKitsAdapter: DNAKitsAdapter
    private lateinit var dnaOrdersAdapter: DNAOrdersAdapter
    private var dnaKitTypes: List<DNAKitType> = emptyList()
    private var dnaOrders: List<DNAOrder> = emptyList()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityDnaprofilingBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "DNA Profiling"
        
        authRepository = AuthRepository(this)
        
        setupRecyclerViews()
        loadDNAData()
    }
    
    private fun setupRecyclerViews() {
        // DNA Kits horizontal RecyclerView
        dnaKitsAdapter = DNAKitsAdapter(dnaKitTypes) { kit ->
            handleKitOrder(kit)
        }
        binding.rvDNAKits.layoutManager = LinearLayoutManager(this, LinearLayoutManager.HORIZONTAL, false)
        binding.rvDNAKits.adapter = dnaKitsAdapter
        
        // DNA Orders vertical RecyclerView
        dnaOrdersAdapter = DNAOrdersAdapter(dnaOrders) { order ->
            handleShowReport(order)
        }
        binding.rvDNAOrders.layoutManager = LinearLayoutManager(this)
        binding.rvDNAOrders.adapter = dnaOrdersAdapter
    }
    
    private fun loadDNAData() {
        lifecycleScope.launch {
            try {
                val token = authRepository.getAccessToken()
                if (token == null) {
                    showError("Please login to view DNA profiling information")
                    return@launch
                }
                
                val apiService = RetrofitClient.createApiServiceWithToken(token)
                
                // Fetch DNA Kit Types
                val kitsResponse = apiService.getDNAKitTypes()
                if (kitsResponse.isSuccessful && kitsResponse.body() != null) {
                    val paginatedResponse = kitsResponse.body()!!
                    dnaKitTypes = paginatedResponse.results ?: emptyList()
                    android.util.Log.d("DNAProfiling", "Loaded ${dnaKitTypes.size} DNA kit types")
                    dnaKitsAdapter.updateKits(dnaKitTypes)
                } else {
                    android.util.Log.e("DNAProfiling", "Failed to load kit types: ${kitsResponse.code()}")
                }
                
                // Fetch DNA Orders
                val ordersResponse = apiService.getDNAOrders()
                if (ordersResponse.isSuccessful && ordersResponse.body() != null) {
                    val paginatedResponse = ordersResponse.body()!!
                    dnaOrders = paginatedResponse.results ?: emptyList()
                    android.util.Log.d("DNAProfiling", "Loaded ${dnaOrders.size} DNA orders")
                    dnaOrdersAdapter.updateOrders(dnaOrders)
                    
                    // Show/hide no orders message
                    if (dnaOrders.isEmpty()) {
                        binding.tvNoOrders.visibility = View.VISIBLE
                        binding.rvDNAOrders.visibility = View.GONE
                    } else {
                        binding.tvNoOrders.visibility = View.GONE
                        binding.rvDNAOrders.visibility = View.VISIBLE
                    }
                } else {
                    android.util.Log.e("DNAProfiling", "Failed to load orders: ${ordersResponse.code()}")
                    binding.tvNoOrders.visibility = View.VISIBLE
                    binding.rvDNAOrders.visibility = View.GONE
                }
                
            } catch (e: Exception) {
                android.util.Log.e("DNAProfiling", "Failed to load DNA data: ${e.message}", e)
                showError("Failed to load DNA profiling information: ${e.message}")
            }
        }
    }
    
    private fun handleKitOrder(kit: DNAKitType) {
        Toast.makeText(this, "Order DNA Kit feature coming soon. Kit: ${kit.name}", Toast.LENGTH_SHORT).show()
        // TODO: Implement DNA kit ordering with shipping address modal
    }
    
    private fun handleShowReport(order: DNAOrder) {
        val orderId = order.id
        if (orderId == null) {
            Toast.makeText(this, "Unable to load report: Order ID not found", Toast.LENGTH_SHORT).show()
            return
        }
        
        // Find the adapter position and toggle report visibility
        val position = dnaOrders.indexOf(order)
        if (position != -1) {
            val wasExpanded = dnaOrdersAdapter.isReportExpanded(position)
            dnaOrdersAdapter.toggleReport(position, orderId)
            
            // If expanding and report not cached, fetch it
            if (!wasExpanded) {
                fetchDNAReport(orderId, position)
            }
        }
    }
    
    private fun fetchDNAReport(orderId: Int, position: Int) {
        lifecycleScope.launch {
            try {
                val token = authRepository.getAccessToken()
                if (token == null) {
                    Toast.makeText(this@DNAProfilingActivity, "Please login to view DNA reports", Toast.LENGTH_SHORT).show()
                    return@launch
                }
                
                val apiService = RetrofitClient.createApiServiceWithToken(token)
                val reportResponse = apiService.getDNAReport(orderId)
                
                if (reportResponse.isSuccessful && reportResponse.body() != null) {
                    val report = reportResponse.body()!!
                    dnaOrdersAdapter.setReportForOrder(orderId, report, position)
                } else {
                    android.util.Log.e("DNAProfiling", "Failed to load report: ${reportResponse.code()}")
                    Toast.makeText(this@DNAProfilingActivity, "Failed to load DNA report", Toast.LENGTH_SHORT).show()
                    // Collapse the report section on error
                    dnaOrdersAdapter.toggleReport(position, orderId)
                }
            } catch (e: Exception) {
                android.util.Log.e("DNAProfiling", "Failed to fetch DNA report: ${e.message}", e)
                Toast.makeText(this@DNAProfilingActivity, "Failed to load DNA report: ${e.message}", Toast.LENGTH_SHORT).show()
                // Collapse the report section on error
                dnaOrdersAdapter.toggleReport(position, orderId)
            }
        }
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

class DNAKitsAdapter(
    private var kits: List<DNAKitType>,
    private val onKitOrder: (DNAKitType) -> Unit
) : RecyclerView.Adapter<DNAKitsAdapter.KitViewHolder>() {
    
    fun updateKits(newKits: List<DNAKitType>) {
        kits = newKits
        notifyDataSetChanged()
    }
    
    class KitViewHolder(val binding: ItemDnaKitBinding) : RecyclerView.ViewHolder(binding.root)
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): KitViewHolder {
        val binding = ItemDnaKitBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return KitViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: KitViewHolder, position: Int) {
        val kit = kits[position]
        
        holder.binding.tvKitName.text = kit.name ?: "N/A"
        holder.binding.tvKitCategory.text = kit.category ?: "N/A"
        holder.binding.tvKitDescription.text = kit.description ?: ""
        holder.binding.tvKitPrice.text = "₹${kit.price ?: "0"}"
        holder.binding.tvProcessingTime.text = "${kit.processingTimeDays ?: 0} days"
        
        // Parse and display features
        val features = parseFeatures(kit.features)
        val featuresAdapter = KitFeaturesAdapter(features)
        holder.binding.rvKitFeatures.layoutManager = LinearLayoutManager(holder.itemView.context)
        holder.binding.rvKitFeatures.adapter = featuresAdapter
        
        holder.binding.btnOrderKit.setOnClickListener {
            onKitOrder(kit)
        }
    }
    
    override fun getItemCount() = kits.size
    
    private fun parseFeatures(features: Any?): List<String> {
        if (features == null) return emptyList()
        
        return when (features) {
            is List<*> -> features.mapNotNull { it?.toString() }
            is String -> features.split(",").map { it.trim() }.filter { it.isNotEmpty() }
            else -> listOf(features.toString())
        }
    }
}

class KitFeaturesAdapter(private val features: List<String>) : RecyclerView.Adapter<KitFeaturesAdapter.FeatureViewHolder>() {
    
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

class DNAOrdersAdapter(
    private var orders: List<DNAOrder>,
    private val onShowReport: (DNAOrder) -> Unit
) : RecyclerView.Adapter<DNAOrdersAdapter.OrderViewHolder>() {
    
    private val expandedReports = mutableSetOf<Int>() // Store positions of expanded reports
    private val reportCache = mutableMapOf<Int, DNAReport>() // Cache fetched reports
    
    fun updateOrders(newOrders: List<DNAOrder>) {
        orders = newOrders
        notifyDataSetChanged()
    }
    
    fun isReportExpanded(position: Int): Boolean {
        return expandedReports.contains(position)
    }
    
    fun toggleReport(position: Int, @Suppress("UNUSED_PARAMETER") orderId: Int) {
        if (expandedReports.contains(position)) {
            // Collapse
            expandedReports.remove(position)
            notifyItemChanged(position)
        } else {
            // Expand
            expandedReports.add(position)
            notifyItemChanged(position)
        }
    }
    
    class OrderViewHolder(val binding: ItemDnaOrderDetailBinding) : RecyclerView.ViewHolder(binding.root)
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): OrderViewHolder {
        val binding = ItemDnaOrderDetailBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return OrderViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: OrderViewHolder, position: Int) {
        val order = orders[position]
        
        holder.binding.tvOrderKitName.text = order.kitTypeName ?: "Unknown Kit"
        holder.binding.tvOrderId.text = order.orderId ?: "N/A"
        holder.binding.tvOrderAmount.text = "₹${order.totalAmount ?: "0"}"
        holder.binding.tvOrderDate.text = formatDate(order.orderDate)
        holder.binding.tvOrderCategory.text = order.kitCategory ?: "N/A"
        
        // Set status text and background
        val status = order.status ?: "UNKNOWN"
        holder.binding.tvOrderStatus.text = status
        val statusBackground = when (status) {
            "COMPLETED", "RESULTS_GENERATED" -> R.drawable.bg_status_completed
            "PROCESSING" -> R.drawable.bg_status_processing
            "PENDING" -> R.drawable.bg_status_pending
            else -> R.drawable.bg_status_pending
        }
        holder.binding.tvOrderStatus.background = ContextCompat.getDrawable(holder.itemView.context, statusBackground)
        
        // Show/hide "Show Report" button based on status
        val showReportButton = status == "RESULTS_GENERATED" || status == "COMPLETED"
        holder.binding.btnShowReport.visibility = if (showReportButton) View.VISIBLE else View.GONE
        
        // Set up button click listener
        holder.binding.btnShowReport.setOnClickListener {
            onShowReport(order)
        }
        
        // Handle report expansion
        val isExpanded = expandedReports.contains(position)
        holder.binding.llReportContent.visibility = if (isExpanded) View.VISIBLE else View.GONE
        
        if (isExpanded) {
            val orderId = order.id
            if (orderId != null) {
                val cachedReport = reportCache[orderId]
                if (cachedReport != null) {
                    displayReport(holder, cachedReport)
                } else {
                    // Show loading indicator - report will be fetched by activity
                    holder.binding.pbReportLoading.visibility = View.VISIBLE
                    holder.binding.tvReportSummary.visibility = View.GONE
                    holder.binding.rvKeyFindings.visibility = View.GONE
                    holder.binding.tvReportRecommendations.visibility = View.GONE
                    holder.binding.btnViewReportFile.visibility = View.GONE
                    // Hide headers
                    holder.binding.tvKeyFindingsHeader.visibility = View.GONE
                    holder.binding.tvRecommendationsHeader.visibility = View.GONE
                }
            }
        }
    }
    
    
    private fun displayReport(holder: OrderViewHolder, report: DNAReport) {
        holder.binding.pbReportLoading.visibility = View.GONE
        
        // Display summary
        if (!report.summary.isNullOrBlank()) {
            holder.binding.tvReportSummary.text = report.summary
            holder.binding.tvReportSummary.visibility = View.VISIBLE
        } else {
            holder.binding.tvReportSummary.visibility = View.GONE
        }
        
        // Display key findings
        val keyFindings = report.keyFindings
        if (keyFindings != null && keyFindings.isNotEmpty()) {
            val findingsAdapter = KeyFindingsAdapter(keyFindings)
            holder.binding.rvKeyFindings.layoutManager = LinearLayoutManager(holder.itemView.context)
            holder.binding.rvKeyFindings.adapter = findingsAdapter
            holder.binding.rvKeyFindings.visibility = View.VISIBLE
            // Show "Key Findings" header
            holder.binding.tvKeyFindingsHeader.visibility = View.VISIBLE
        } else {
            holder.binding.rvKeyFindings.visibility = View.GONE
            holder.binding.tvKeyFindingsHeader.visibility = View.GONE
        }
        
        // Display recommendations
        if (!report.recommendations.isNullOrBlank()) {
            holder.binding.tvReportRecommendations.text = report.recommendations
            holder.binding.tvReportRecommendations.visibility = View.VISIBLE
            // Show "Recommendations" header
            holder.binding.tvRecommendationsHeader.visibility = View.VISIBLE
        } else {
            holder.binding.tvReportRecommendations.visibility = View.GONE
            holder.binding.tvRecommendationsHeader.visibility = View.GONE
        }
        
        // Display report file URL button if available
        if (!report.reportFileUrl.isNullOrBlank()) {
            holder.binding.btnViewReportFile.visibility = View.VISIBLE
            holder.binding.btnViewReportFile.setOnClickListener {
                val intent = Intent(Intent.ACTION_VIEW, Uri.parse(report.reportFileUrl))
                holder.itemView.context.startActivity(intent)
            }
        } else {
            holder.binding.btnViewReportFile.visibility = View.GONE
        }
    }
    
    fun setReportForOrder(orderId: Int, report: DNAReport, position: Int) {
        reportCache[orderId] = report
        notifyItemChanged(position)
    }
    
    override fun getItemCount() = orders.size
    
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
}

class KeyFindingsAdapter(private val findings: List<Any>) : RecyclerView.Adapter<KeyFindingsAdapter.FindingViewHolder>() {
    
    class FindingViewHolder(val binding: ItemKeyFindingBinding) : RecyclerView.ViewHolder(binding.root)
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): FindingViewHolder {
        val binding = ItemKeyFindingBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return FindingViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: FindingViewHolder, position: Int) {
        val finding = findings[position]
        
        try {
            when (finding) {
                is Map<*, *> -> {
                    val trait = finding["trait"]?.toString() 
                        ?: finding["trait_name"]?.toString() 
                        ?: "Unknown Trait"
                    val value = finding["value"]?.toString() ?: "N/A"
                    
                    holder.binding.tvFindingTrait.text = trait
                    holder.binding.tvFindingValue.text = "Value: $value"
                }
                is String -> {
                    // If it's already a string, try to parse it or display as is
                    holder.binding.tvFindingTrait.text = "Finding"
                    holder.binding.tvFindingValue.text = finding
                }
                else -> {
                    holder.binding.tvFindingTrait.text = "Finding"
                    holder.binding.tvFindingValue.text = finding.toString()
                }
            }
        } catch (e: Exception) {
            android.util.Log.e("KeyFindingsAdapter", "Error displaying finding: ${e.message}", e)
            holder.binding.tvFindingTrait.text = "Error"
            holder.binding.tvFindingValue.text = "Unable to display finding"
        }
    }
    
    override fun getItemCount() = findings.size
}
