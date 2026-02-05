package com.aevum.health.data.models

import com.google.gson.annotations.SerializedName

data class SubscriptionPlan(
    @SerializedName("id")
    val id: Int? = null,
    
    @SerializedName("name")
    val name: String? = null,
    
    @SerializedName("description")
    val description: String? = null,
    
    @SerializedName("price")
    val price: String? = null,
    
    @SerializedName("billing_cycle")
    val billingCycle: String? = null,
    
    @SerializedName("duration_months")
    val durationMonths: Int? = null,
    
    @SerializedName("features")
    val features: Any? = null, // Can be array, string, or object
    
    @SerializedName("is_active")
    val isActive: Boolean? = null
)

