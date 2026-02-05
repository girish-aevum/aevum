package com.aevum.health

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.aevum.health.repository.AuthRepository
import com.aevum.health.ui.auth.LoginActivity
import com.aevum.health.ui.dashboard.DashboardActivity
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    
    private lateinit var authRepository: AuthRepository
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        authRepository = AuthRepository(this)
        
        // Check authentication status and redirect
        lifecycleScope.launch {
            if (authRepository.isLoggedIn()) {
                // User is logged in, go to dashboard
                startActivity(Intent(this@MainActivity, DashboardActivity::class.java))
            } else {
                // User is not logged in, go to login
                startActivity(Intent(this@MainActivity, LoginActivity::class.java))
            }
            finish()
        }
    }
}

