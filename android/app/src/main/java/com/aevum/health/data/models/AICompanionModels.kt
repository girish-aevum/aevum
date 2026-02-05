package com.aevum.health.data.models

import com.google.gson.annotations.SerializedName

// Request models
data class CreateThreadRequest(
    @SerializedName("title") val title: String,
    @SerializedName("category") val category: String = "MENTAL_HEALTH"
)

data class ChatMessageRequest(
    @SerializedName("thread_id") val threadId: String,
    @SerializedName("message") val message: String,
    @SerializedName("workflow_type") val workflowType: String? = null
)

// Response models
data class CreateThreadResponse(
    @SerializedName("thread_id") val threadId: String? = null,
    @SerializedName("title") val title: String? = null,
    @SerializedName("category") val category: String? = null,
    @SerializedName("created_at") val createdAt: String? = null
)

data class MessageData(
    @SerializedName("content") val content: String,
    @SerializedName("sender") val sender: String,
    @SerializedName("created_at") val createdAt: String?
)

data class ChatMessageResponse(
    @SerializedName("thread_id") val threadId: String,
    @SerializedName("workflow_id") val workflowId: String?,
    @SerializedName("workflow_type") val workflowType: String?,
    @SerializedName("workflow_stage") val workflowStage: String?,
    @SerializedName("user_message") val userMessage: MessageData,
    @SerializedName("ai_response") val aiResponse: MessageData,
    @SerializedName("ai_summary") val aiSummary: String?,
    @SerializedName("thread_title") val threadTitle: String?
)

data class RawAIResponse(
    @SerializedName("text") val text: String,
    @SerializedName("status") val status: String?,
    @SerializedName("rag_enabled") val ragEnabled: Boolean? = null,
    @SerializedName("rag_sources") val ragSources: List<String>? = null
)

