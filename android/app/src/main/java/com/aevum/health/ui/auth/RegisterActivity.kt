package com.aevum.health.ui.auth

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.aevum.health.databinding.ActivityRegisterBinding
import com.aevum.health.repository.AuthRepository
import com.aevum.health.ui.dashboard.DashboardActivity
import kotlinx.coroutines.launch

class RegisterActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityRegisterBinding
    private lateinit var authRepository: AuthRepository
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityRegisterBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        authRepository = AuthRepository(this)
        
        setupClickListeners()
    }
    
    private fun setupClickListeners() {
        binding.btnRegister.setOnClickListener {
            performRegister()
        }
        
        binding.tvLogin.setOnClickListener {
            finish()
        }
    }
    
    private fun performRegister() {
        val email = binding.etEmail.text.toString().trim()
        val password = binding.etPassword.text.toString()
        val confirmPassword = binding.etConfirmPassword.text.toString()
        val firstName = binding.etFirstName.text.toString().trim()
        val lastName = binding.etLastName.text.toString().trim()
        
        if (email.isEmpty() || password.isEmpty() || confirmPassword.isEmpty()) {
            Toast.makeText(this, "Please fill in all required fields", Toast.LENGTH_SHORT).show()
            return
        }
        
        if (password != confirmPassword) {
            Toast.makeText(this, "Passwords do not match", Toast.LENGTH_SHORT).show()
            return
        }
        
        if (password.length < 8) {
            Toast.makeText(this, "Password must be at least 8 characters", Toast.LENGTH_SHORT).show()
            return
        }
        
        binding.btnRegister.isEnabled = false
        binding.progressBar.visibility = android.view.View.VISIBLE
        
        lifecycleScope.launch {
            val result = authRepository.register(
                email = email,
                password = password,
                firstName = if (firstName.isNotEmpty()) firstName else null,
                lastName = if (lastName.isNotEmpty()) lastName else null
            )
            
            binding.btnRegister.isEnabled = true
            binding.progressBar.visibility = android.view.View.GONE
            
            result.onSuccess { _ ->
                Toast.makeText(this@RegisterActivity, "Registration successful!", Toast.LENGTH_SHORT).show()
                startActivity(Intent(this@RegisterActivity, DashboardActivity::class.java))
                finish()
            }.onFailure { exception ->
                Toast.makeText(this@RegisterActivity, exception.message ?: "Registration failed", Toast.LENGTH_LONG).show()
            }
        }
    }
}

