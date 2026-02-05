package com.aevum.health.data.models

import com.google.gson.annotations.SerializedName

data class SubscriptionData(
    @SerializedName("id")
    val id: Int? = null,
    
    @SerializedName("user")
    val user: Int? = null,
    
    @SerializedName("plan")
    val plan: SubscriptionPlan? = null,
    
    @SerializedName("start_date")
    val startDate: String? = null,
    
    @SerializedName("end_date")
    val endDate: String? = null,
    
    @SerializedName("status")
    val status: String? = null,
    
    @SerializedName("auto_renew")
    val autoRenew: Boolean? = null,
    
    @SerializedName("payment_status")
    val paymentStatus: String? = null,
    
    @SerializedName("last_payment_date")
    val lastPaymentDate: String? = null,
    
    @SerializedName("next_billing_date")
    val nextBillingDate: String? = null,
    
    @SerializedName("created_at")
    val createdAt: String? = null,
    
    @SerializedName("updated_at")
    val updatedAt: String? = null
)

