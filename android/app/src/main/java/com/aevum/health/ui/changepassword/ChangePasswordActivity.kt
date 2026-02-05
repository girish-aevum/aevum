package com.aevum.health.ui.changepassword

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.aevum.health.databinding.ActivityChangePasswordBinding
import com.aevum.health.network.RetrofitClient
import com.aevum.health.repository.AuthRepository
import kotlinx.coroutines.launch

class ChangePasswordActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityChangePasswordBinding
    private lateinit var authRepository: AuthRepository
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityChangePasswordBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // Enable back button
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Change Password"
        
        authRepository = AuthRepository(this)
        
        setupClickListeners()
    }
    
    private fun setupClickListeners() {
        binding.btnChangePassword.setOnClickListener {
            changePassword()
        }
    }
    
    private fun changePassword() {
        val currentPassword = binding.etCurrentPassword.text.toString()
        val newPassword = binding.etNewPassword.text.toString()
        val confirmPassword = binding.etConfirmPassword.text.toString()
        
        if (currentPassword.isEmpty() || newPassword.isEmpty() || confirmPassword.isEmpty()) {
            Toast.makeText(this, "Please fill in all fields", Toast.LENGTH_SHORT).show()
            return
        }
        
        if (newPassword != confirmPassword) {
            Toast.makeText(this, "New passwords do not match", Toast.LENGTH_SHORT).show()
            return
        }
        
        if (newPassword.length < 8) {
            Toast.makeText(this, "Password must be at least 8 characters", Toast.LENGTH_SHORT).show()
            return
        }
        
        lifecycleScope.launch {
            try {
                val token = authRepository.getAccessToken()
                if (token == null) {
                    Toast.makeText(this@ChangePasswordActivity, "Please login", Toast.LENGTH_SHORT).show()
                    return@launch
                }
                
                val apiService = RetrofitClient.createApiServiceWithToken(token)
                val response = apiService.changePassword(
                    "Bearer $token",
                    mapOf(
                        "old_password" to currentPassword,
                        "new_password" to newPassword
                    )
                )
                
                if (response.isSuccessful) {
                    Toast.makeText(this@ChangePasswordActivity, "Password changed successfully", Toast.LENGTH_SHORT).show()
                    finish()
                } else {
                    Toast.makeText(this@ChangePasswordActivity, "Failed to change password", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@ChangePasswordActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        onBackPressedDispatcher.onBackPressed()
        return true
    }
}

