package com.aevum.health.data.models

import com.google.gson.annotations.SerializedName

data class User(
    @SerializedName("id")
    val id: Int? = null,
    
    @SerializedName("username")
    val username: String? = null,
    
    @SerializedName("email")
    val email: String? = null,
    
    @SerializedName("first_name")
    val firstName: String? = null,
    
    @SerializedName("last_name")
    val lastName: String? = null,
    
    @SerializedName("full_name")
    val fullName: String? = null,
    
    @SerializedName("is_active")
    val isActive: Boolean? = null,
    
    @SerializedName("date_joined")
    val dateJoined: String? = null,
    
    @SerializedName("last_login")
    val lastLogin: String? = null
)

