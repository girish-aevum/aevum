package com.aevum.health.network

import com.aevum.health.data.models.CreateThreadRequest
import com.aevum.health.data.models.CreateThreadResponse
import com.aevum.health.data.models.ChatMessageRequest
import com.aevum.health.data.models.ChatMessageResponse
import com.aevum.health.data.models.CreateJournalEntryRequest
import com.aevum.health.data.models.RawAIResponse
import com.aevum.health.data.models.UserProfile
import com.aevum.health.data.models.DNAOrder
import com.aevum.health.data.models.DNAKitType
import com.aevum.health.data.models.DNAReport
import com.aevum.health.data.models.SubscriptionPlan
import com.aevum.health.data.models.JournalEntry
import com.aevum.health.data.models.JournalEntryDetail
import com.aevum.health.data.models.JournalCategory
import com.aevum.health.data.models.JournalTemplate
import com.aevum.health.data.models.JournalStreak
import com.aevum.health.data.models.JournalInsight
import com.aevum.health.data.models.JournalReminder
import com.aevum.health.data.models.QuickJournalEntryRequest
import com.aevum.health.data.models.LoginRequest
import com.aevum.health.data.models.RegisterRequest
import com.aevum.health.data.models.AuthResponse
import com.aevum.health.data.models.ApiResponse
import com.aevum.health.data.models.User
import com.aevum.health.data.models.SubscriptionData
import com.aevum.health.data.models.PaginatedResponse
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    
    // Authentication endpoints
    @POST("authentication/login/")
    suspend fun login(@Body request: LoginRequest): Response<AuthResponse>
    
    @POST("authentication/register/")
    suspend fun register(@Body request: RegisterRequest): Response<ApiResponse<AuthResponse>>
    
    @POST("authentication/logout/")
    suspend fun logout(@Header("Authorization") token: String): Response<ApiResponse<Unit>>
    
    @GET("authentication/profile/")
    suspend fun getProfile(): Response<UserProfile>
    
    @PUT("authentication/profile/")
    suspend fun updateProfile(
        @Header("Authorization") token: String,
        @Body user: User
    ): Response<ApiResponse<User>>
    
    @POST("authentication/forgot-password/")
    suspend fun forgotPassword(@Body email: Map<String, String>): Response<ApiResponse<Unit>>
    
    @POST("authentication/reset-password/")
    suspend fun resetPassword(@Body data: Map<String, String>): Response<ApiResponse<Unit>>
    
    @POST("authentication/change-password/")
    suspend fun changePassword(
        @Header("Authorization") token: String,
        @Body data: Map<String, String>
    ): Response<ApiResponse<Unit>>
    
    // Subscription endpoints
    @GET("authentication/subscription/my-subscription/")
    suspend fun getMySubscription(): Response<SubscriptionData>
    
    @GET("authentication/subscription/plans/")
    suspend fun getSubscriptionPlans(
        @Query("page") page: Int? = null,
        @Query("page_size") pageSize: Int? = null
    ): Response<PaginatedResponse<SubscriptionPlan>>
    
    // Dashboard endpoints
    @GET("dashboard/health-summary/")
    suspend fun getHealthSummary(@Header("Authorization") token: String): Response<ApiResponse<Any>>
    
    // Mental Wellness endpoints
    @GET("mental-wellness/mood-entries/")
    suspend fun getMoodEntries(
        @Header("Authorization") token: String,
        @Query("page") page: Int? = null,
        @Query("page_size") pageSize: Int? = null
    ): Response<PaginatedResponse<Any>>
    
    // AI Companion endpoints (use createApiServiceWithToken - no Authorization header needed)
    @POST("ai-companion/threads/")
    suspend fun createThread(
        @Body request: CreateThreadRequest
    ): Response<CreateThreadResponse>
    
    @GET("ai-companion/threads/")
    suspend fun getThreads(
        @Query("page") page: Int? = null,
        @Query("page_size") pageSize: Int? = null
    ): Response<PaginatedResponse<Any>>
    
    @POST("ai-companion/chat/")
    suspend fun sendChatMessage(
        @Body request: ChatMessageRequest
    ): Response<ChatMessageResponse>
    
    @POST("ai-companion/ai-companion-raw/")
    suspend fun sendRawMessage(
        @Body request: Map<String, String>
    ): Response<RawAIResponse>
    
    // DNA Profile endpoints
    @GET("dna-profile/kit-types/")
    suspend fun getDNAKitTypes(
        @Query("page") page: Int? = null,
        @Query("page_size") pageSize: Int? = null
    ): Response<PaginatedResponse<DNAKitType>>
    
    @GET("dna-profile/orders/")
    suspend fun getDNAOrders(
        @Query("page") page: Int? = null,
        @Query("page_size") pageSize: Int? = null
    ): Response<PaginatedResponse<DNAOrder>>
    
    @GET("dna-profile/reports/{orderId}/")
    suspend fun getDNAReport(@Path("orderId") orderId: Int): Response<DNAReport>
    
    // Smart Journal endpoints
    @GET("smart-journal/entries/")
    suspend fun getJournalEntries(
        @Query("page") page: Int? = null,
        @Query("page_size") pageSize: Int? = null,
        @Query("limit") limit: Int? = null,
        @Query("start_date") startDate: String? = null,
        @Query("end_date") endDate: String? = null
    ): Response<PaginatedResponse<JournalEntry>>

    @POST("smart-journal/entries/quick-create/")
    suspend fun createQuickJournalEntry(
        @Body request: QuickJournalEntryRequest
    ): Response<JournalEntryDetail>

    @POST("smart-journal/entries/create/")
    suspend fun createJournalEntry(
        @Body request: CreateJournalEntryRequest
    ): Response<JournalEntryDetail>

    @GET("smart-journal/entries/{entryId}/")
    suspend fun getJournalEntryDetail(
        @Path("entryId") entryId: String
    ): Response<JournalEntryDetail>

    @GET("smart-journal/streak/")
    suspend fun getJournalStreak(): Response<JournalStreak>

    @GET("smart-journal/reminders/")
    suspend fun getJournalReminders(): Response<PaginatedResponse<JournalReminder>>

    @GET("smart-journal/insights/")
    suspend fun getJournalInsights(
        @Query("limit") limit: Int? = null
    ): Response<PaginatedResponse<JournalInsight>>

    @GET("smart-journal/categories/")
    suspend fun getJournalCategories(
        @Query("limit") limit: Int? = null
    ): Response<PaginatedResponse<JournalCategory>>

    @GET("smart-journal/templates/")
    suspend fun getJournalTemplates(
        @Query("limit") limit: Int? = null
    ): Response<PaginatedResponse<JournalTemplate>>
}
