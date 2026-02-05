package com.aevum.health.network

import android.util.Log
import com.aevum.health.BuildConfig
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.Response
import okhttp3.ResponseBody.Companion.toResponseBody
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {
    private const val TIMEOUT_SECONDS = 30L
    private const val TAG = "RetrofitClient"
    
    private val gson: Gson = GsonBuilder()
        .setLenient()
        .serializeNulls()
        .setPrettyPrinting()
        .create()
    
    // Custom interceptor to log raw response body
    private val responseLoggingInterceptor = Interceptor { chain ->
        val request = chain.request()
        val response = chain.proceed(request)
        
        // Log raw response for profile endpoint
        if (request.url.encodedPath.contains("profile")) {
            val responseBody = response.body
            val source = responseBody?.source()
            source?.request(Long.MAX_VALUE) // Buffer the entire response
            val buffer = source?.buffer
            
            // Clone buffer and read for logging
            val clonedBuffer = buffer?.clone()
            val rawResponse = clonedBuffer?.readUtf8()
            
            // Print raw response - this will appear in Logcat
            android.util.Log.e(TAG, "=========================================")
            android.util.Log.e(TAG, "RAW API RESPONSE for ${request.url}")
            android.util.Log.e(TAG, "Response Code: ${response.code}")
            android.util.Log.e(TAG, "Response Body: $rawResponse")
            android.util.Log.e(TAG, "=========================================")
            
            // Also print to console for easier viewing
            println("=========================================")
            println("RAW API RESPONSE for ${request.url}")
            println("Response Code: ${response.code}")
            println("Response Body: $rawResponse")
            println("=========================================")
            
            // Create a new response body from the cloned buffer (original buffer is consumed)
            val contentType = responseBody?.contentType()
            val newResponseBody = rawResponse?.toResponseBody(contentType)
            
            return@Interceptor response.newBuilder()
                .body(newResponseBody)
                .build()
        }
        
        response
    }
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = if (BuildConfig.DEBUG) {
            HttpLoggingInterceptor.Level.BODY
        } else {
            HttpLoggingInterceptor.Level.NONE
        }
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(responseLoggingInterceptor)
        .addInterceptor(loggingInterceptor)
        .connectTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
        .readTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
        .writeTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
        .build()
    
    private val retrofit = Retrofit.Builder()
        .baseUrl(if (BuildConfig.API_BASE_URL.endsWith("/")) BuildConfig.API_BASE_URL else "${BuildConfig.API_BASE_URL}/")
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create(gson))
        .build()
    
    val apiService: ApiService = retrofit.create(ApiService::class.java)
    
    /**
     * Create an ApiService with a custom authorization token interceptor
     */
    fun createApiServiceWithToken(token: String): ApiService {
        val authInterceptor = Interceptor { chain ->
            val originalRequest = chain.request()
            val newRequest = originalRequest.newBuilder()
                .header("Authorization", "Bearer $token")
                .build()
            chain.proceed(newRequest)
        }
        
        val clientWithAuth = okHttpClient.newBuilder()
            .addInterceptor(authInterceptor)
            .build()
        
        val retrofitWithAuth = retrofit.newBuilder()
            .client(clientWithAuth)
            .build()
        
        return retrofitWithAuth.create(ApiService::class.java)
    }
}

