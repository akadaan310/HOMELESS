package world.homeless.rendezvous

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.media.AudioAttributes
import android.media.AudioFocusRequest
import android.media.AudioManager
import android.os.Build
import android.os.Bundle
import android.os.Vibrator
import android.os.VibrationEffect
import android.webkit.JavascriptInterface
import android.view.View
import android.view.WindowInsets
import android.view.WindowInsetsController
import android.webkit.PermissionRequest
import com.getcapacitor.BridgeWebChromeClient
import com.getcapacitor.BridgeActivity

/** Native lifecycle for the exact same offline-capable PlayCanvas application. */
class MainActivity : BridgeActivity() {
    private lateinit var audioManager: AudioManager
    private var focusRequest: AudioFocusRequest? = null
    private var pendingMicrophone: PermissionRequest? = null
    private val listener = AudioManager.OnAudioFocusChangeListener { focus ->
        runOnUiThread { bridge.webView.evaluateJavascript("window.HomelessNative?.audioFocus(${focus == AudioManager.AUDIOFOCUS_GAIN})", null) }
    }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        audioManager = getSystemService(Context.AUDIO_SERVICE) as AudioManager
        bridge.webView.settings.mediaPlaybackRequiresUserGesture = true
        bridge.webView.webChromeClient = object : BridgeWebChromeClient(bridge) {
            override fun onPermissionRequest(request: PermissionRequest) {
                runOnUiThread {
                    // Local bundled app can request the microphone only after an explicit gesture.
                    if (request.origin.toString() != "https://localhost/" && request.origin.toString() != "https://localhost") {
                        request.deny(); return@runOnUiThread
                    }
                    if (!request.resources.contains(PermissionRequest.RESOURCE_AUDIO_CAPTURE)) {
                        request.deny(); return@runOnUiThread
                    }
                    if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                        request.grant(arrayOf(PermissionRequest.RESOURCE_AUDIO_CAPTURE))
                    } else {
                        pendingMicrophone?.deny()
                        pendingMicrophone = request
                        requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), 701)
                    }
                }
            }
        }
        bridge.webView.addJavascriptInterface(object {
            @JavascriptInterface fun impact() {
                val vibrator = getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
                if (Build.VERSION.SDK_INT >= 26) vibrator.vibrate(VibrationEffect.createOneShot(18, 55))
                else { @Suppress("DEPRECATION") vibrator.vibrate(18) }
            }
        }, "HomelessHaptics")
        immersive()
    }
    private fun immersive() {
        if (Build.VERSION.SDK_INT >= 30) {
            window.setDecorFitsSystemWindows(false)
            window.insetsController?.apply {
                hide(WindowInsets.Type.statusBars() or WindowInsets.Type.navigationBars())
                systemBarsBehavior = WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            }
        } else {
            @Suppress("DEPRECATION")
            window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY or View.SYSTEM_UI_FLAG_FULLSCREEN or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or View.SYSTEM_UI_FLAG_LAYOUT_STABLE or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
        }
    }
    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 701) {
            if (grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED) pendingMicrophone?.grant(arrayOf(PermissionRequest.RESOURCE_AUDIO_CAPTURE))
            else pendingMicrophone?.deny()
            pendingMicrophone = null
        }
    }
    override fun onResume() {
        super.onResume()
        if (::audioManager.isInitialized) {
            if (Build.VERSION.SDK_INT >= 26) {
                focusRequest = AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN)
                    .setAudioAttributes(AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_GAME).setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build())
                    .setOnAudioFocusChangeListener(listener).build()
                audioManager.requestAudioFocus(focusRequest!!)
            } else { @Suppress("DEPRECATION") audioManager.requestAudioFocus(listener, AudioManager.STREAM_MUSIC, AudioManager.AUDIOFOCUS_GAIN) }
        }
        bridge.webView.evaluateJavascript("window.HomelessNative?.resume()", null)
        immersive()
    }
    override fun onPause() {
        bridge.webView.evaluateJavascript("window.HomelessNative?.pause()", null)
        if (::audioManager.isInitialized) {
            if (Build.VERSION.SDK_INT >= 26) focusRequest?.let { audioManager.abandonAudioFocusRequest(it) }
            else { @Suppress("DEPRECATION") audioManager.abandonAudioFocus(listener) }
        }
        super.onPause()
    }
}
