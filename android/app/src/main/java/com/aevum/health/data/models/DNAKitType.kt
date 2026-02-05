package com.aevum.health.data.models

import com.google.gson.annotations.SerializedName

data class DNAKitType(
    @SerializedName("id")
    val id: Int? = null,
    
    @SerializedName("name")
    val name: String? = null,
    
    @SerializedName("category")
    val category: String? = null,
    
    @SerializedName("description")
    val description: String? = null,
    
    @SerializedName("price")
    val price: String? = null,
    
    @SerializedName("processing_time_days")
    val processingTimeDays: Int? = null,
    
    @SerializedName("features")
    val features: Any? = null // Can be array, string, or object
)

