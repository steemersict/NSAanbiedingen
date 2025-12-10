use serde_json::json;
use std::sync::Arc;
use tauri::{AppHandle, Emitter, Manager, State};
use tauri_plugin_shell::process::CommandEvent;
use tauri_plugin_shell::ShellExt;
use tokio::sync::RwLock;

/// Global state to store backend port
#[derive(Default, Clone)]
pub struct BackendState {
    port: Arc<RwLock<Option<u16>>>,
}

/// Get the backend port (called from frontend)
#[tauri::command]
async fn get_backend_port(state: State<'_, BackendState>) -> Result<u16, String> {
    let port = state.port.read().await;
    port.ok_or_else(|| "Backend not ready".to_string())
}

/// Initialize and start the backend sidecar
async fn start_backend_sidecar(app: AppHandle, state: BackendState) {
    let shell = app.shell();

    // Spawn the backend sidecar process
    match shell.sidecar("backend") {
        Ok(sidecar_command) => {
            println!("[Tauri] Backend sidecar command created");

            match sidecar_command.spawn() {
                Ok((mut rx, _child)) => {
                    println!("[Tauri] Backend sidecar spawned, waiting for SERVER_PORT...");

                    // Listen to stdout for port announcement
                    while let Some(event) = rx.recv().await {
                        match event {
                            CommandEvent::Stdout(line) => {
                                let text = String::from_utf8_lossy(&line);

                                // Check for SERVER_PORT pattern
                                if let Some(port_str) = text.strip_prefix("SERVER_PORT=") {
                                    if let Ok(port) = port_str.trim().parse::<u16>() {
                                        println!("[Tauri] Backend ready on port {}", port);

                                        // Store port in state
                                        *state.port.write().await = Some(port);

                                        // Emit event to frontend
                                        if let Err(e) = app.emit("backend-ready", json!({ "port": port })) {
                                            eprintln!("[Tauri] Failed to emit backend-ready event: {}", e);
                                        }

                                        // Log other stdout messages but don't break on them
                                    }
                                } else if !text.is_empty() {
                                    println!("[Backend] {}", text);
                                }
                            }
                            CommandEvent::Stderr(line) => {
                                let text = String::from_utf8_lossy(&line);
                                eprintln!("[Backend stderr] {}", text);
                            }
                            CommandEvent::Error(err) => {
                                eprintln!("[Tauri] Backend error: {}", err);
                                break;
                            }
                            CommandEvent::Terminated(payload) => {
                                eprintln!("[Tauri] Backend terminated with code {:?}", payload.code);
                                break;
                            }
                            _ => {}
                        }
                    }
                }
                Err(e) => {
                    eprintln!("[Tauri] Failed to spawn backend sidecar: {}", e);
                }
            }
        }
        Err(e) => {
            eprintln!("[Tauri] Failed to create backend sidecar command: {}", e);
        }
    }
}

/// Main Tauri application entry point
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .manage(BackendState::default())
        .setup(|app| {
            let app_handle = app.handle().clone();
            let state: State<BackendState> = app.state::<BackendState>();
            let state_clone = state.inner().clone();

            // Spawn backend in background task
            tauri::async_runtime::spawn(start_backend_sidecar(
                app_handle,
                state_clone,
            ));

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_backend_port])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
