package com.aevum.health.data.models

import com.google.gson.annotations.SerializedName

data class UserProfile(
    @SerializedName("id")
    val id: Int? = null,
    
    @SerializedName("user")
    val user: User? = null,
    
    // Profile Image
    @SerializedName("profile_image")
    val profileImage: String? = null,
    
    @SerializedName("profile_image_url")
    val profileImageUrl: String? = null,
    
    // Demographics
    @SerializedName("date_of_birth")
    val dateOfBirth: String? = null,
    
    @SerializedName("sex")
    val sex: String? = null,
    
    @SerializedName("gender_identity")
    val genderIdentity: String? = null,
    
    @SerializedName("blood_group")
    val bloodGroup: String? = null,
    
    // Physical metrics
    @SerializedName("height_cm")
    val heightCm: Float? = null,
    
    @SerializedName("weight_kg")
    val weightKg: Float? = null,
    
    @SerializedName("waist_cm")
    val waistCm: Float? = null,
    
    @SerializedName("hip_cm")
    val hipCm: Float? = null,
    
    // Contact & address
    @SerializedName("phone_number")
    val phoneNumber: String? = null,
    
    @SerializedName("address_line1")
    val addressLine1: String? = null,
    
    @SerializedName("address_line2")
    val addressLine2: String? = null,
    
    @SerializedName("city")
    val city: String? = null,
    
    @SerializedName("state")
    val state: String? = null,
    
    @SerializedName("country")
    val country: String? = null,
    
    @SerializedName("postal_code")
    val postalCode: String? = null,
    
    @SerializedName("occupation")
    val occupation: String? = null,
    
    // Lifestyle
    @SerializedName("smoking_status")
    val smokingStatus: String? = null,
    
    @SerializedName("alcohol_use")
    val alcoholUse: String? = null,
    
    @SerializedName("physical_activity_level")
    val physicalActivityLevel: String? = null,
    
    @SerializedName("diet_type")
    val dietType: String? = null,
    
    @SerializedName("sleep_hours")
    val sleepHours: Float? = null,
    
    @SerializedName("stress_level")
    val stressLevel: String? = null,
    
    // Medical history
    @SerializedName("chronic_conditions")
    val chronicConditions: String? = null,
    
    @SerializedName("surgeries")
    val surgeries: String? = null,
    
    @SerializedName("allergies")
    val allergies: String? = null,
    
    @SerializedName("medications_current")
    val medicationsCurrent: String? = null,
    
    @SerializedName("family_history")
    val familyHistory: String? = null,
    
    @SerializedName("vaccinations")
    val vaccinations: String? = null,
    
    // Reproductive health
    @SerializedName("reproductive_health_notes")
    val reproductiveHealthNotes: String? = null,
    
    // Care team
    @SerializedName("primary_physician_name")
    val primaryPhysicianName: String? = null,
    
    @SerializedName("primary_physician_contact")
    val primaryPhysicianContact: String? = null,
    
    // Insurance
    @SerializedName("insurance_provider")
    val insuranceProvider: String? = null,
    
    @SerializedName("insurance_policy_number")
    val insurancePolicyNumber: String? = null,
    
    // Emergency contact
    @SerializedName("emergency_contact_name")
    val emergencyContactName: String? = null,
    
    @SerializedName("emergency_contact_relationship")
    val emergencyContactRelationship: String? = null,
    
    @SerializedName("emergency_contact_phone")
    val emergencyContactPhone: String? = null,
    
    // Preferences & consents
    @SerializedName("preferred_hospital")
    val preferredHospital: String? = null,
    
    @SerializedName("communication_preferences")
    val communicationPreferences: String? = null,
    
    @SerializedName("language_preferences")
    val languagePreferences: String? = null,
    
    @SerializedName("data_sharing_consent")
    val dataSharingConsent: Boolean? = null,
    
    @SerializedName("research_consent")
    val researchConsent: Boolean? = null,
    
    // Cross-domain IDs
    @SerializedName("dna_profile_id")
    val dnaProfileId: String? = null,
    
    // Timestamps
    @SerializedName("created_at")
    val createdAt: String? = null,
    
    @SerializedName("updated_at")
    val updatedAt: String? = null
)

