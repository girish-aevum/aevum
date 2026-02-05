package com.aevum.health.ui.profile

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.aevum.health.databinding.ActivityProfileBinding
import com.aevum.health.repository.AuthRepository
import kotlinx.coroutines.launch

class ProfileActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityProfileBinding
    private lateinit var authRepository: AuthRepository
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityProfileBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // Enable back button
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Profile"
        
        authRepository = AuthRepository(this)
        
        loadProfile()
    }
    
    override fun onSupportNavigateUp(): Boolean {
        onBackPressedDispatcher.onBackPressed()
        return true
    }
    
    private fun loadProfile() {
        // Show loading state
        binding.tvName.text = "Loading..."
        binding.tvEmail.text = "Loading..."
        binding.tvUsername.text = "Loading..."
        
        lifecycleScope.launch {
            try {
                android.util.Log.d("ProfileActivity", "Starting to load profile...")
                val result = authRepository.getProfile()
                
                result.onSuccess { profile ->
                    android.util.Log.d("ProfileActivity", "Profile loaded successfully")
                    android.util.Log.d("ProfileActivity", "Profile user: ${profile.user?.email}")
                    
                    val user = profile.user
                    if (user != null) {
                        // Build full name from first_name and last_name, or use full_name if available
                        val fullName = user.fullName?.takeIf { it.isNotBlank() } ?: buildString {
                            if (!user.firstName.isNullOrBlank()) {
                                append(user.firstName)
                            }
                            if (!user.lastName.isNullOrBlank()) {
                                if (isNotEmpty()) append(" ")
                                append(user.lastName)
                            }
                            if (isEmpty()) {
                                append(user.username ?: "User")
                            }
                        }.trim()
                        
                        binding.tvName.text = fullName.ifEmpty { "N/A" }
                        binding.tvEmail.text = user.email ?: "N/A"
                        binding.tvUsername.text = user.username ?: "N/A"
                    } else {
                        android.util.Log.w("ProfileActivity", "User data is null in profile")
                        binding.tvName.text = "N/A"
                        binding.tvEmail.text = "N/A"
                        binding.tvUsername.text = "N/A"
                    }
                    
                    // Set phone number
                    binding.tvPhoneNumber.text = profile.phoneNumber?.takeIf { it.isNotBlank() } ?: "N/A"
                    
                    // Set date of birth - format it nicely if available
                    binding.tvDateOfBirth.text = profile.dateOfBirth?.takeIf { it.isNotBlank() } ?: "N/A"
                    
                    // Set blood group
                    binding.tvBloodGroup.text = profile.bloodGroup?.takeIf { it.isNotBlank() } ?: "N/A"
                    
                    // Physical Metrics
                    val heightText = profile.heightCm?.let { "${it} cm" } ?: "N/A"
                    binding.tvHeight.text = heightText
                    
                    val weightText = profile.weightKg?.let { "${it} kg" } ?: "N/A"
                    binding.tvWeight.text = weightText
                    
                    // Lifestyle
                    binding.tvOccupation.text = profile.occupation?.takeIf { it.isNotBlank() } ?: "N/A"
                    binding.tvSmokingStatus.text = profile.smokingStatus?.takeIf { it.isNotBlank() } ?: "N/A"
                    binding.tvPhysicalActivity.text = profile.physicalActivityLevel?.takeIf { it.isNotBlank() } ?: "N/A"
                    
                    // Build address string
                    val addressParts = mutableListOf<String>()
                    profile.addressLine1?.let { if (it.isNotBlank()) addressParts.add(it) }
                    profile.addressLine2?.let { if (it.isNotBlank()) addressParts.add(it) }
                    profile.city?.let { if (it.isNotBlank()) addressParts.add(it) }
                    profile.state?.let { if (it.isNotBlank()) addressParts.add(it) }
                    profile.postalCode?.let { if (it.isNotBlank()) addressParts.add(it) }
                    profile.country?.let { if (it.isNotBlank()) addressParts.add(it) }
                    
                    binding.tvAddress.text = if (addressParts.isNotEmpty()) {
                        addressParts.joinToString("\n")
                    } else {
                        "N/A"
                    }
                    
                    // Emergency Contact
                    binding.tvEmergencyContactName.text = profile.emergencyContactName?.takeIf { it.isNotBlank() } ?: "N/A"
                    binding.tvEmergencyContactRelationship.text = profile.emergencyContactRelationship?.takeIf { it.isNotBlank() } ?: "N/A"
                    binding.tvEmergencyContactPhone.text = profile.emergencyContactPhone?.takeIf { it.isNotBlank() } ?: "N/A"
                    
                    android.util.Log.d("ProfileActivity", "Profile display updated successfully")
                }.onFailure { exception ->
                    android.util.Log.e("ProfileActivity", "Failed to load profile", exception)
                    android.util.Log.e("ProfileActivity", "Error message: ${exception.message}")
                    android.util.Log.e("ProfileActivity", "Error cause: ${exception.cause}")
                    
                    // Set error state
                    binding.tvName.text = "Error"
                    binding.tvEmail.text = "Failed to load"
                    binding.tvUsername.text = "N/A"
                    
                    // Show user-friendly error message
                    val errorMessage = when {
                        exception.message?.contains("Network", ignoreCase = true) == true -> 
                            "Network error. Please check your connection."
                        exception.message?.contains("parse", ignoreCase = true) == true -> 
                            "Data format error. Please try again."
                        exception.message?.contains("authenticated", ignoreCase = true) == true -> 
                            "Session expired. Please login again."
                        else -> 
                            "Failed to load profile. Please try again."
                    }
                    
                    Toast.makeText(this@ProfileActivity, errorMessage, Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                android.util.Log.e("ProfileActivity", "Unexpected error in loadProfile", e)
                Toast.makeText(this@ProfileActivity, "An unexpected error occurred. Please try again.", Toast.LENGTH_LONG).show()
            }
        }
    }
}

