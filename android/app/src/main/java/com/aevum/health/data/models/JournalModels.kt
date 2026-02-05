package com.aevum.health.data.models

import com.google.gson.annotations.SerializedName

data class JournalEntry(
    @SerializedName("entry_id") val entryId: String?,
    @SerializedName("title") val title: String?,
    @SerializedName("content_preview") val contentPreview: String?,
    @SerializedName("category_name") val categoryName: String?,
    @SerializedName("category_color") val categoryColor: String?,
    @SerializedName("template_name") val templateName: String?,
    @SerializedName("entry_date") val entryDate: String?,
    @SerializedName("mood_rating") val moodRating: Int?,
    @SerializedName("mood_emoji") val moodEmoji: String?,
    @SerializedName("energy_level") val energyLevel: Int?,
    @SerializedName("energy_emoji") val energyEmoji: String?,
    @SerializedName("location") val location: String?,
    @SerializedName("privacy_level") val privacyLevel: String?,
    @SerializedName("is_favorite") val isFavorite: Boolean?,
    @SerializedName("is_archived") val isArchived: Boolean?,
    @SerializedName("is_draft") val isDraft: Boolean?,
    @SerializedName("word_count") val wordCount: Int?,
    @SerializedName("estimated_reading_time") val estimatedReadingTime: Int?,
    @SerializedName("tags") val tags: List<String>?,
    @SerializedName("attachment_count") val attachmentCount: Int?,
    @SerializedName("days_ago") val daysAgo: String?,
    @SerializedName("created_at") val createdAt: String?,
    @SerializedName("updated_at") val updatedAt: String?
)

data class JournalEntryDetail(
    @SerializedName("entry_id") val entryId: String?,
    @SerializedName("title") val title: String?,
    @SerializedName("content") val content: String?,
    @SerializedName("category") val category: JournalCategory?,
    @SerializedName("template") val template: JournalTemplate?,
    @SerializedName("tags") val tags: List<JournalTag>?,
    @SerializedName("entry_date") val entryDate: String?,
    @SerializedName("mood_rating") val moodRating: Int?,
    @SerializedName("mood_emoji") val moodEmoji: String?,
    @SerializedName("energy_level") val energyLevel: Int?,
    @SerializedName("energy_emoji") val energyEmoji: String?,
    @SerializedName("location") val location: String?,
    @SerializedName("weather") val weather: String?,
    @SerializedName("privacy_level") val privacyLevel: String?,
    @SerializedName("is_favorite") val isFavorite: Boolean?,
    @SerializedName("is_archived") val isArchived: Boolean?,
    @SerializedName("is_draft") val isDraft: Boolean?,
    @SerializedName("word_count") val wordCount: Int?,
    @SerializedName("estimated_reading_time") val estimatedReadingTime: Int?,
    @SerializedName("sentiment_score") val sentimentScore: Double?,
    @SerializedName("ai_insights") val aiInsights: Map<String, Any>?,
    @SerializedName("created_at") val createdAt: String?,
    @SerializedName("updated_at") val updatedAt: String?
)

data class JournalCategory(
    @SerializedName("id") val id: Int?,
    @SerializedName("name") val name: String?,
    @SerializedName("description") val description: String?,
    @SerializedName("color_hex") val colorHex: String?,
    @SerializedName("entry_count") val entryCount: Int?
)

data class JournalTemplate(
    @SerializedName("id") val id: Int?,
    @SerializedName("name") val name: String?,
    @SerializedName("template_type") val templateType: String?,
    @SerializedName("description") val description: String?,
    @SerializedName("prompt_questions") val promptQuestions: List<String>?,
    @SerializedName("default_structure") val defaultStructure: Map<String, Any>?,
    @SerializedName("is_public") val isPublic: Boolean?,
    @SerializedName("is_active") val isActive: Boolean?
)

data class JournalTag(
    @SerializedName("id") val id: Int?,
    @SerializedName("name") val name: String?,
    @SerializedName("color_hex") val colorHex: String?
)

data class JournalStreak(
    @SerializedName("current_streak") val currentStreak: Int?,
    @SerializedName("longest_streak") val longestStreak: Int?,
    @SerializedName("total_entries") val totalEntries: Int?,
    @SerializedName("last_entry_date") val lastEntryDate: String?,
    @SerializedName("milestones_achieved") val milestonesAchieved: List<Milestone>?,
    @SerializedName("streak_status") val streakStatus: String?,
    @SerializedName("next_milestone") val nextMilestone: NextMilestone?
)

data class Milestone(
    @SerializedName("milestone") val milestone: String?,
    @SerializedName("achieved_at") val achievedAt: String?
)

data class NextMilestone(
    @SerializedName("target") val target: Int?,
    @SerializedName("remaining") val remaining: Int?,
    @SerializedName("type") val type: String?
)

data class JournalReminder(
    @SerializedName("id") val id: Int?,
    @SerializedName("title") val title: String?,
    @SerializedName("message") val message: String?,
    @SerializedName("reminder_type_display") val reminderTypeDisplay: String?,
    @SerializedName("frequency_display") val frequencyDisplay: String?,
    @SerializedName("reminder_time") val reminderTime: String?,
    @SerializedName("next_reminder_display") val nextReminderDisplay: String?
)

data class JournalInsight(
    @SerializedName("id") val id: Int?,
    @SerializedName("insight_type_display") val insightTypeDisplay: String?,
    @SerializedName("title") val title: String?,
    @SerializedName("description") val description: String?,
    @SerializedName("generated_at") val generatedAt: String?,
    @SerializedName("confidence_score") val confidenceScore: Double?
)

data class QuickJournalEntryRequest(
    @SerializedName("content") val content: String,
    @SerializedName("mood_rating") val moodRating: Int
)

data class CreateJournalEntryRequest(
    @SerializedName("title") val title: String,
    @SerializedName("content") val content: String,
    @SerializedName("mood_rating") val moodRating: Int,
    @SerializedName("energy_level") val energyLevel: Int,
    @SerializedName("privacy_level") val privacyLevel: String,
    @SerializedName("is_favorite") val isFavorite: Boolean,
    @SerializedName("is_draft") val isDraft: Boolean,
    @SerializedName("tag_names") val tagNames: List<String>,
    @SerializedName("category") val category: Int?,
    @SerializedName("template") val template: Int?,
    @SerializedName("location") val location: String?,
    @SerializedName("weather") val weather: String?
)

