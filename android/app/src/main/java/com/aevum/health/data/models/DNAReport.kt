package com.aevum.health.data.models

import com.google.gson.annotations.SerializedName

data class DNAReport(
    @SerializedName("id")
    val id: Int? = null,
    
    @SerializedName("kit_type_name")
    val kitTypeName: String? = null,
    
    @SerializedName("kit_order_id")
    val kitOrderId: String? = null,
    
    @SerializedName("report_type")
    val reportType: String? = null,
    
    @SerializedName("status")
    val status: String? = null,
    
    @SerializedName("generated_date")
    val generatedDate: String? = null,
    
    @SerializedName("report_file_url")
    val reportFileUrl: String? = null,
    
    @SerializedName("raw_data_url")
    val rawDataUrl: String? = null,
    
    @SerializedName("summary")
    val summary: String? = null,
    
    @SerializedName("key_findings")
    val keyFindings: List<Any>? = null,
    
    @SerializedName("recommendations")
    val recommendations: String? = null,
    
    @SerializedName("quality_score")
    val qualityScore: String? = null,
    
    @SerializedName("validated_by")
    val validatedBy: String? = null,
    
    @SerializedName("validation_date")
    val validationDate: String? = null,
    
    @SerializedName("created_at")
    val createdAt: String? = null,
    
    @SerializedName("updated_at")
    val updatedAt: String? = null
)

