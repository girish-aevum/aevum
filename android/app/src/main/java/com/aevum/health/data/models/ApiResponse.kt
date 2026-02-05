package com.aevum.health.data.models

import com.google.gson.annotations.SerializedName

data class ApiResponse<T>(
    @SerializedName("message")
    val message: String? = null,
    
    @SerializedName("error")
    val error: String? = null,
    
    @SerializedName("data")
    val data: T? = null
)

data class PaginatedResponse<T>(
    @SerializedName("pagination")
    val pagination: Pagination? = null,
    
    @SerializedName("results")
    val results: List<T>? = null
)

data class Pagination(
    @SerializedName("count")
    val count: Int,
    
    @SerializedName("total_pages")
    val totalPages: Int,
    
    @SerializedName("current_page")
    val currentPage: Int,
    
    @SerializedName("page_size")
    val pageSize: Int,
    
    @SerializedName("has_next")
    val hasNext: Boolean,
    
    @SerializedName("has_previous")
    val hasPrevious: Boolean,
    
    @SerializedName("next_page")
    val nextPage: Int?,
    
    @SerializedName("previous_page")
    val previousPage: Int?
)

