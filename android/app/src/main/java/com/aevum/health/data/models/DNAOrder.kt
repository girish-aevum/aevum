package com.aevum.health.data.models

import com.google.gson.annotations.SerializedName

data class DNAOrder(
    @SerializedName("id")
    val id: Int? = null,
    
    @SerializedName("order_id")
    val orderId: String? = null,
    
    @SerializedName("kit_type")
    val kitType: Int? = null,
    
    @SerializedName("kit_type_name")
    val kitTypeName: String? = null,
    
    @SerializedName("kit_category")
    val kitCategory: String? = null,
    
    @SerializedName("kit_id")
    val kitId: String? = null,
    
    @SerializedName("status")
    val status: String? = null,
    
    @SerializedName("quantity")
    val quantity: Int? = null,
    
    @SerializedName("total_amount")
    val totalAmount: String? = null,
    
    @SerializedName("order_date")
    val orderDate: String? = null,
    
    @SerializedName("estimated_completion_date")
    val estimatedCompletionDate: String? = null,
    
    @SerializedName("shipping_method")
    val shippingMethod: String? = null,
    
    @SerializedName("shipping_address")
    val shippingAddress: Map<String, Any>? = null,
    
    @SerializedName("report_url")
    val reportUrl: String? = null
)

