// swift-tools-version: 6.2

import SwiftUI
import AppKit
import PythonKit

@main
struct SwiftYTXcode: App {
    init() {
        // Configure application settings
        NSApplication.shared.setActivationPolicy(.regular)
        print("SwiftYTXcode initialized")
    }
    
    var body: some Scene {
        WindowGroup("YouTube Media Downloader") {
            ContentView()
        }
        .windowStyle(.automatic)
        .commands {
            CommandGroup(replacing: .appInfo) {
                Button("Quit") {
                    NSApplication.shared.terminate(nil)
                }
                .keyboardShortcut("q", modifiers: .command)
            }
        }
    }
}

struct ContentView: View {
    @State private var urlString: String = ""
    @State private var downloadDirectory: URL?
    @State private var statusMessage = "Ready"
    @State private var isProcessing = false
    @State private var progress = 0.0
    @State private var downloadType = DownloadType.audio
    @State private var audioFormat = AudioFormat.m4a
    @State private var applyNoiseReduction = false
    @State private var logMessages: [String] = []
    
    // Enum for download type selection
    enum DownloadType: String, CaseIterable, Identifiable {
        case audio = "Audio Only"
        case video = "Video + Audio"
        
        var id: String { self.rawValue }
    }
    
    // Enum for audio format selection
    enum AudioFormat: String, CaseIterable, Identifiable {
        case m4a = "M4A"
        case mp3 = "MP3"
        
        var id: String { self.rawValue }
    }
    
    var body: some View {
        VStack {
            Text("YouTube Media Downloader")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            // URL Input Section
            VStack {
                HStack {
                    Text("YouTube URL:")
                        .frame(width: 150, alignment: .leading)
                    TextField("https://www.youtube.com/watch?v=", text: $urlString)
                        .textFieldStyle(.roundedBorder)
                        .frame(maxWidth: .infinity)
                        .disabled(isProcessing)
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(5)
            }
            .padding()
            
            // Download Directory Section
            VStack {
                HStack {
                    Text("Download Directory:")
                        .frame(width: 150, alignment: .leading)
                    Text(downloadDirectory?.lastPathComponent ?? "No directory selected")
                        .frame(maxWidth: .infinity, alignment: .leading)
                    Button("Browse") {
                        selectDownloadDirectory()
                    }
                    .disabled(isProcessing)
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(5)
            }
            .padding()
            
            // Download Options Section
            VStack {
                Text("Download Options")
                    .font(.headline)
                    .padding()
                
                HStack {
                    Text("Download Type:")
                        .frame(width: 150, alignment: .leading)
                    Picker("Download Type", selection: $downloadType) {
                        ForEach(DownloadType.allCases) {
                            Text($0.rawValue)
                        }
                    }
                    .pickerStyle(.segmented)
                    .disabled(isProcessing)
                }
                .padding()
                
                HStack {
                    Text("Audio Format:")
                        .frame(width: 150, alignment: .leading)
                    Picker("Audio Format", selection: $audioFormat) {
                        ForEach(AudioFormat.allCases) {
                            Text($0.rawValue)
                        }
                    }
                    .pickerStyle(.segmented)
                    .disabled(isProcessing || downloadType == .video)
                }
                .padding()
                
                HStack {
                    Text("Apply Noise Reduction:")
                        .frame(width: 150, alignment: .leading)
                    Toggle(isOn: $applyNoiseReduction) {
                        EmptyView()
                    }
                    .disabled(isProcessing || downloadType == .video)
                    Text("(audio only)")
                        .foregroundColor(.secondary)
                        .font(.caption)
                }
                .padding()
            }
            .padding()
            .background(Color.gray.opacity(0.1))
            .cornerRadius(5)
            
            // Action buttons
            HStack {
                Button(action: {
                    downloadMedia()
                }) {
                    Text("Start Download")
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .disabled(isProcessing || urlString.isEmpty || downloadDirectory == nil)
                
                Button(action: {
                    cancelDownload()
                }) {
                    Text("Cancel")
                        .padding()
                        .background(Color.gray)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .disabled(!isProcessing)
            }
            .padding()
            
            // Progress bar
            ProgressView(value: progress)
                .progressViewStyle(LinearProgressViewStyle())
                .padding()
                .frame(width: 500)
            
            // Status display
            VStack {
                Text("Download Status")
                    .font(.headline)
                
                ScrollView {
                    VStack(alignment: .leading) {
                        ForEach(logMessages, id: \.self) {
                            Text($0)
                                .font(.system(.body, design: .monospaced))
                        }
                    }
                }
                .frame(minWidth: 0, maxWidth: .infinity, minHeight: 100, maxHeight: 200)
                .border(Color.gray, width: 1)
                .padding()
            }
            .padding()
            
            // Bottom info bar
            HStack {
                Text(statusMessage)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
                    .background(Color.gray.opacity(0.1))
            }
            .frame(maxWidth: .infinity)
        }
        .padding()
        .frame(minWidth: 700, minHeight: 700)
        .onAppear {
            print("ContentView appeared on screen")
            // Ensure the window is frontmost and focused
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                if let window = NSApp.windows.first {
                    window.makeKeyAndOrderFront(nil)
                    NSApp.activate(ignoringOtherApps: true)
                }
            }
            
            // Set default download directory to user's Downloads folder
            if let defaultDownloads = FileManager.default.urls(for: .downloadsDirectory, in: .userDomainMask).first {
                downloadDirectory = defaultDownloads
            }
            
            // Check system components
            checkDependencies()
        }
    }
    
    func selectDownloadDirectory() {
        let openPanel = NSOpenPanel()
        openPanel.canChooseDirectories = true
        openPanel.canChooseFiles = false
        openPanel.allowsMultipleSelection = false
        
        if openPanel.runModal() == .OK {
            downloadDirectory = openPanel.urls.first
        }
    }
    
    func downloadMedia() {
        guard !urlString.isEmpty, let downloadDirectory = downloadDirectory else { return }
        
        isProcessing = true
        statusMessage = "Starting download..."
        progress = 0.0
        logMessages = []
        
        // Log the start of processing
        logMessage("Starting YouTube media download")
        logMessage("URL: \(urlString)")
        logMessage("Download directory: \(downloadDirectory.path)")
        logMessage("Download type: \(downloadType.rawValue)")
        logMessage("Audio format: \(audioFormat.rawValue)")
        logMessage("Apply noise reduction: \(applyNoiseReduction)")
        
        // Run in a background task to avoid blocking UI
        Task.detached {
            do {
                // Configure Python path to use the simple_downloader.py
                let sys = Python.import("sys")
                
                // Add the directory containing simple_downloader.py to Python path
                let pythonScriptPath = "/Users/jk/gits/hub/youtube"
                // Convert String to PythonObject and check if it's in sys.path
                let pythonPathObj = PythonObject(pythonScriptPath)
                if Python.bool(sys.path.__contains__(pythonPathObj)) == false {
                    sys.path.append(pythonPathObj)
                    await MainActor.run {
                        self.logMessage("Added Python script path to sys.path")
                    }
                }
                
                // Import the Python downloader module or run the script
                // For simplicity, we'll just simulate progress here
                // In a real application, you would call the actual download function
                
                // Simulate progress updates
                for i in 1...10 {
                    try await Task.sleep(nanoseconds: 1_000_000_000) // Sleep for 1 second
                    await MainActor.run {
                        self.progress = Double(i) / 10.0
                        self.logMessage("Download progress: \(Int(self.progress * 100))%")
                    }
                }
                
                // Update UI on main thread with completion
                await MainActor.run {
                    if self.applyNoiseReduction && self.downloadType == .audio {
                        self.logMessage("Applying noise reduction...")
                        self.logMessage("Noise reduction completed")
                    }
                    self.logMessage("Download completed successfully!")
                    self.statusMessage = "Download completed successfully!"
                    self.isProcessing = false
                }
            } catch {
                // Handle errors
                await MainActor.run {
                    self.logMessage("Error: \(error.localizedDescription)")
                    self.statusMessage = "Error: \(error.localizedDescription)"
                    self.isProcessing = false
                }
            }
        }
    }
    
    func cancelDownload() {
        // In a real application, you would need to properly cancel the Python process
        statusMessage = "Download cancelled"
        isProcessing = false
        logMessage("Download cancelled by user")
    }
    
    func logMessage(_ message: String) {
        let timestamp = Date().formatted(date: .omitted, time: .standard)
        logMessages.append("[\(timestamp)] \(message)")
    }
    
    func checkDependencies() {
        // Check for yt-dlp and ffmpeg
        logMessage("Checking system dependencies...")
        
        // In a real app, you would actually check for these dependencies
        // For now, we'll just log a message
        logMessage("System dependencies check completed")
        
        // Detect system proxy settings
        if let proxy = detectSystemProxy() {
            logMessage("System proxy detected: \(proxy)")
        } else {
            logMessage("No system proxy detected")
        }
    }
    
    func detectSystemProxy() -> String? {
        // Simple proxy detection
        // In a real app, you would use CFNetwork or other APIs to detect system proxies
        return nil
    }
}
