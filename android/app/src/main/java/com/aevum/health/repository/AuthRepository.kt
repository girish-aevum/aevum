package com.aevum.health.repository

import android.content.Context
import com.aevum.health.data.local.AuthPreferences
import com.aevum.health.data.models.*
import com.aevum.health.network.ApiService
import com.aevum.health.network.RetrofitClient
import kotlinx.coroutines.flow.first
import retrofit2.HttpException
import java.io.IOException

class AuthRepository(private val context: Context) {
    
    private val authPreferences = AuthPreferences(context)
    private val apiService = RetrofitClient.apiService
    
    suspend fun login(email: String, password: String): Result<User> {
        return try {
            val response = apiService.login(LoginRequest(username = email, password = password))
            
            if (response.isSuccessful && response.body() != null) {
                val authResponse = response.body()!!
                
                // Save tokens
                authPreferences.saveTokens(
                    authResponse.tokens.access,
                    authResponse.tokens.refresh
                )
                
                // Save user info
                authPreferences.saveUserInfo(
                    authResponse.user.id?.toString() ?: "",
                    authResponse.user.email ?: "",
                    "${authResponse.user.firstName ?: ""} ${authResponse.user.lastName ?: ""}".trim().takeIf { it.isNotEmpty() } ?: authResponse.user.username ?: authResponse.user.email ?: "User"
                )
                
                Result.success(authResponse.user)
            } else {
                val errorMessage = when (response.code()) {
                    401 -> "Invalid email or password"
                    400 -> "Bad request. Please check your input."
                    else -> response.message() ?: "Login failed"
                }
                Result.failure(Exception(errorMessage))
            }
        } catch (e: HttpException) {
            Result.failure(Exception("Server error: ${e.message()}"))
        } catch (e: IOException) {
            Result.failure(Exception("Network error. Please check your connection."))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun register(
        email: String,
        password: String,
        firstName: String? = null,
        lastName: String? = null
    ): Result<User> {
        return try {
            val response = apiService.register(
                RegisterRequest(
                    email = email,
                    password = password,
                    firstName = firstName,
                    lastName = lastName
                )
            )
            
            if (response.isSuccessful && response.body() != null) {
                val apiResponse = response.body()!!
                if (apiResponse.data != null) {
                    val authResponse = apiResponse.data
                    
                    // Save tokens
                    authPreferences.saveTokens(
                        authResponse.tokens.access,
                        authResponse.tokens.refresh
                    )
                    
                    // Save user info
                    authPreferences.saveUserInfo(
                        authResponse.user.id?.toString() ?: "",
                        authResponse.user.email ?: "",
                        "${authResponse.user.firstName ?: ""} ${authResponse.user.lastName ?: ""}".trim().takeIf { it.isNotEmpty() } ?: authResponse.user.username ?: authResponse.user.email ?: "User"
                    )
                    
                    Result.success(authResponse.user)
                } else {
                    Result.failure(Exception(apiResponse.error ?: "Registration failed"))
                }
            } else {
                val errorMessage = response.message() ?: "Registration failed"
                Result.failure(Exception(errorMessage))
            }
        } catch (e: HttpException) {
            Result.failure(Exception("Server error: ${e.message()}"))
        } catch (e: IOException) {
            Result.failure(Exception("Network error. Please check your connection."))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun logout(): Result<Unit> {
        return try {
            val token = authPreferences.getAccessToken()
            if (token != null) {
                apiService.logout("Bearer $token")
            }
            authPreferences.clearAuth()
            Result.success(Unit)
        } catch (e: Exception) {
            // Clear auth even if API call fails
            authPreferences.clearAuth()
            Result.success(Unit)
        }
    }
    
    suspend fun getProfile(): Result<UserProfile> {
        return try {
            val token = authPreferences.getAccessToken()
            if (token == null) {
                android.util.Log.w("AuthRepository", "getProfile: No access token found")
                return Result.failure(Exception("Not authenticated. Please login again."))
            }
            
            android.util.Log.d("AuthRepository", "getProfile: Fetching profile with token: ${token.take(20)}...")
            val apiServiceWithAuth = RetrofitClient.createApiServiceWithToken(token)
            val response = apiServiceWithAuth.getProfile()
            
            android.util.Log.e("AuthRepository", "getProfile: Response code: ${response.code()}, isSuccessful: ${response.isSuccessful}")
            
            if (response.isSuccessful) {
                try {
                    val body = response.body()
                    android.util.Log.e("AuthRepository", "getProfile: Attempting to parse response body...")
                    if (body != null) {
                        android.util.Log.e("AuthRepository", "getProfile: ✅ Successfully parsed profile!")
                        android.util.Log.e("AuthRepository", "getProfile: User email: ${body.user?.email ?: "null"}")
                        android.util.Log.e("AuthRepository", "getProfile: Profile ID: ${body.id}, User ID: ${body.user?.id}")
                        Result.success(body)
                    } else {
                        android.util.Log.e("AuthRepository", "getProfile: ❌ Response body is null after parsing")
                        Result.failure(Exception("Empty response from server"))
                    }
                } catch (e: Exception) {
                    android.util.Log.e("AuthRepository", "getProfile: ❌❌❌ PARSING ERROR: ${e.message}", e)
                    android.util.Log.e("AuthRepository", "getProfile: Error type: ${e.javaClass.name}")
                    android.util.Log.e("AuthRepository", "getProfile: Stack trace: ${e.stackTraceToString()}")
                    Result.failure(e)
                }
            } else {
                val errorBody = try {
                    val errorString = response.errorBody()?.string()
                    android.util.Log.e("AuthRepository", "getProfile: Error response body: $errorString")
                    errorString ?: "Unknown error"
                } catch (e: Exception) {
                    android.util.Log.e("AuthRepository", "getProfile: Error reading error body: ${e.message}", e)
                    "Error reading response: ${e.message}"
                }
                Result.failure(Exception("Failed to get profile (${response.code()}): $errorBody"))
            }
        } catch (e: HttpException) {
            android.util.Log.e("AuthRepository", "getProfile: HTTP error", e)
            android.util.Log.e("AuthRepository", "getProfile: HTTP code: ${e.code()}, message: ${e.message()}")
            val errorBody = try {
                e.response()?.errorBody()?.string() ?: "No error body"
            } catch (ex: Exception) {
                "Error reading error body: ${ex.message}"
            }
            android.util.Log.e("AuthRepository", "getProfile: Error body: $errorBody")
            Result.failure(Exception("Server error (${e.code()}): ${e.message()}"))
        } catch (e: IOException) {
            android.util.Log.e("AuthRepository", "getProfile: Network error", e)
            Result.failure(Exception("Network error. Please check your internet connection."))
        } catch (e: IllegalStateException) {
            android.util.Log.e("AuthRepository", "getProfile: IllegalStateException - Parsing error", e)
            android.util.Log.e("AuthRepository", "getProfile: Exception message: ${e.message}")
            android.util.Log.e("AuthRepository", "getProfile: Exception cause: ${e.cause}")
            android.util.Log.e("AuthRepository", "getProfile: Stack trace: ${e.stackTraceToString()}")
            Result.failure(Exception("Failed to parse profile data. Please try again or contact support."))
        } catch (e: Exception) {
            android.util.Log.e("AuthRepository", "getProfile: Unexpected error", e)
            android.util.Log.e("AuthRepository", "getProfile: Exception type: ${e.javaClass.name}")
            android.util.Log.e("AuthRepository", "getProfile: Exception message: ${e.message}")
            android.util.Log.e("AuthRepository", "getProfile: Stack trace: ${e.stackTraceToString()}")
            Result.failure(Exception("Unexpected error: ${e.message ?: "Unknown error"}"))
        }
    }
    
    suspend fun isLoggedIn(): Boolean {
        return authPreferences.isLoggedIn.first()
    }
    
    suspend fun getAccessToken(): String? {
        return authPreferences.getAccessToken()
    }
}

