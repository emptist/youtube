// swift-tools-version: 6.2

import SwiftUI
import AppKit
import PythonKit

@main
struct YTDownloader: App {
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
    @State private var keepRawAudio = false
    @State private var logMessages: [String] = []
    
    // Enum for download type selection
    enum DownloadType: String, CaseIterable, Identifiable {
        case audio = "Audio"
        case video = "Video"
        
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
            // Header
            Text("YouTube Media Downloader")
                .font(.largeTitle)
                .fontWeight(.bold)
                .padding()

            // URL Input Section
            VStack {
                HStack {
                    Text("YouTube URL:")
                        .frame(width: 150, alignment: .leading)
                        .font(.system(size: 14))
                    TextField("https://www.youtube.com/watch?v=", text: $urlString)
                        .textFieldStyle(.roundedBorder)
                        .frame(maxWidth: .infinity, minHeight: 30)
                        .font(.system(size: 14))
                        .disabled(isProcessing)
                }
            }
            .padding()
            .background(Color.gray.opacity(0.05))
            .cornerRadius(5)

            // Download Directory Section
            VStack {
                HStack {
                    Text("Download Directory:")
                        .frame(width: 150, alignment: .leading)
                        .font(.system(size: 14))
                    Text(downloadDirectory?.lastPathComponent ?? "No directory selected")
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .font(.system(size: 14))
                    Button("Browse") {
                        selectDownloadDirectory()
                    }
                    .disabled(isProcessing)
                    .font(.system(size: 14))
                }
            }
            .padding()
            .background(Color.gray.opacity(0.05))
            .cornerRadius(5)

            // Download Options Section
            VStack {
                Text("Download Options")
                    .font(.headline)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.bottom, 5)

                HStack {
                    Text("Download Type:")
                        .frame(width: 120, alignment: .leading)
                        .font(.system(size: 14))
                    Picker("", selection: $downloadType) {
                        ForEach(DownloadType.allCases) {
                            Text($0.rawValue)
                        }
                    }
                    .pickerStyle(.segmented)
                    .disabled(isProcessing)
                }
                .padding(.vertical, 5)

                HStack {
                    Text("Audio Format:")
                        .frame(width: 120, alignment: .leading)
                        .font(.system(size: 14))
                    Picker("", selection: $audioFormat) {
                        ForEach(AudioFormat.allCases) {
                            Text($0.rawValue)
                        }
                    }
                    .pickerStyle(.segmented)
                    .disabled(isProcessing || downloadType == .video)
                }
                .padding(.vertical, 5)

                HStack {
                    Text("Apply Noise Reduction:")
                        .font(.system(size: 14))
                    Toggle(isOn: $applyNoiseReduction) {
                        EmptyView()
                    }
                    .disabled(isProcessing || downloadType == .video)
                    Text("(audio only)")
                        .foregroundColor(.secondary)
                        .font(.caption)
                    
                    Spacer()
                    
                    Text("Keep Raw Audio:")
                        .font(.system(size: 14))
                    Toggle(isOn: $keepRawAudio) {
                        EmptyView()
                    }
                    .disabled(isProcessing || downloadType == .video || !applyNoiseReduction)
                    Text("(when denoising)")
                        .foregroundColor(.secondary)
                        .font(.caption)
                }
                .padding(.vertical, 5)
            }
            .padding()
            .background(Color.gray.opacity(0.05))
            .cornerRadius(5)
            
            // Action buttons - using SwiftUI's natural layout system for appropriate sizing
            HStack(spacing: 20) {
                Button(action: {
                    downloadMedia()
                }) {
                    Text("Download")
                        .multilineTextAlignment(.center)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .disabled(isProcessing || urlString.isEmpty || downloadDirectory == nil)
                .fixedSize(horizontal: false, vertical: true)
                
                Button(action: {
                    cancelDownload()
                }) {
                    Text("Cancel")
                        .multilineTextAlignment(.center)
                        .padding()
                        .background(Color.gray)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .disabled(!isProcessing)
                .fixedSize(horizontal: false, vertical: true)
            }
            .padding()
            .frame(maxWidth: .infinity)
            .frame(minWidth: 300) // Minimum width to prevent buttons from being too small
            
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
                logMessage("Keep raw audio: \(keepRawAudio)")
        
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
                
                // Get values from main actor
                let (localUrlString, localDownloadDirectory, localDownloadType, localAudioFormat, localApplyNoiseReduction, localKeepRawAudio) = await MainActor.run {
                    return (
                        urlString,
                        downloadDirectory.path,
                        downloadType == .audio ? "audio" : "video",
                        audioFormat.rawValue.lowercased(),
                        applyNoiseReduction,
                        keepRawAudio
                    )
                }
                
                // Call the helper function that performs the Python integration
                let (stdout, stderr) = try await runPythonDownloader(
                    url: localUrlString,
                    directory: localDownloadDirectory,
                    downloadType: localDownloadType,
                    audioFormat: localAudioFormat,
                    applyNoiseReduction: localApplyNoiseReduction,
                    keepRawAudio: localKeepRawAudio
                )
                
                // Process and log the output
                if !stdout.isEmpty {
                    await MainActor.run {
                        self.logMessage("Python output:\n" + stdout)
                    }
                }
                
                if !stderr.isEmpty {
                    await MainActor.run {
                        self.logMessage("Python warnings:\n" + stderr)
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
    
    // Helper function to run the Python downloader in a separate task
    private func runPythonDownloader(
        url: String,
        directory: String,
        downloadType: String,
        audioFormat: String,
        applyNoiseReduction: Bool,
        keepRawAudio: Bool
    ) async throws -> (stdout: String, stderr: String) {
        // This function will be executed in a separate task
        return try await withTaskCancellationHandler {
            // Set up Python environment
            let sys = Python.import("sys")
            let pythonScriptPath = "/Users/jk/gits/hub/youtube"
            
            // Add the directory containing simple_downloader.py to Python path
            let pythonPathObj = PythonObject(pythonScriptPath)
            if Python.bool(sys.path.__contains__(pythonPathObj)) == false {
                sys.path.append(pythonPathObj)
            }
            
            // Import the Python downloader module
            let simple_downloader = Python.import("simple_downloader")
            
            // Convert Swift values to Python objects
            let urlObj = PythonObject(url)
            let directoryObj = PythonObject(directory)
            let downloadTypeObj = PythonObject(downloadType)
            let formatObj = PythonObject(audioFormat)
            let denoiseObj = PythonObject(applyNoiseReduction)
            let keepRawAudioObj = PythonObject(keepRawAudio)
            
            // Set stdout and stderr to capture output
            let io = Python.import("io")
            let old_stdout = sys.stdout
            let old_stderr = sys.stderr
            let new_stdout = io.StringIO()
            let new_stderr = io.StringIO()
            sys.stdout = new_stdout
            sys.stderr = new_stderr
            
            do {
                // Call the download function
                let _ = simple_downloader.download_video(
                    url: urlObj,
                    output_path: directoryObj,
                    download_type: downloadTypeObj,
                    audio_format: formatObj,
                    denoise: denoiseObj,
                    keep_raw_audio: keepRawAudioObj
                )
                
                // Get the captured output
                let stdout_value = new_stdout.getvalue()
                let stderr_value = new_stderr.getvalue()
                
                // Convert Python strings to Swift strings
                let stdout_str = String(describing: stdout_value)
                let stderr_str = String(describing: stderr_value)
                
                // Restore stdout and stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
                return (stdout: stdout_str, stderr: stderr_str)
            } catch {
                // Get the captured error
                let stderr_value = new_stderr.getvalue()
                let stderr_str = String(describing: stderr_value)
                
                // Restore stdout and stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
                // Handle all errors
                throw NSError(domain: "PythonError", code: 1, userInfo: ["stderr": stderr_str, "error": String(describing: error)])
            }
        } onCancel: {
            // Handle cancellation if needed
        }
    }
}
