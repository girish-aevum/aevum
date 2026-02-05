package com.aevum.health.data.models

import com.google.gson.annotations.SerializedName

data class AuthResponse(
    @SerializedName("tokens")
    val tokens: Tokens,
    
    @SerializedName("user")
    val user: User
)

data class Tokens(
    @SerializedName("access")
    val access: String,
    
    @SerializedName("refresh")
    val refresh: String
)

data class LoginRequest(
    val username: String,
    val password: String
)

data class RegisterRequest(
    val email: String,
    val password: String,
    val firstName: String? = null,
    val lastName: String? = null
)

