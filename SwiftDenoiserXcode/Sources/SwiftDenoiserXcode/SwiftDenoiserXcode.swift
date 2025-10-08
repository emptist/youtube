// swift-tools-version: 6.2

import SwiftUI
import PythonKit
import AppKit

@main
struct SwiftDenoiserXcode: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var delegate
    
    var body: some Scene {
        WindowGroup("Audio Noise Reduction Tool") {
            ContentView()
        }
    }
}

// App delegate to set activation policy
class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApplication.shared.setActivationPolicy(.regular)
        NSApplication.shared.activate(ignoringOtherApps: true)
    }
}

struct ContentView: View {
    @State private var inputFile: URL?
    @State private var outputFile: URL?
    @State private var statusMessage = "Ready"
    @State private var isProcessing = false
    @State private var progress = 0.0
    @State private var noiseSampleDuration = 2.0
    @State private var chunkDuration = 30.0
    @State private var keepOriginal = true
    @State private var logMessages: [String] = []
    
    var body: some View {
        VStack {
            Text("Audio Noise Reduction Tool")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            // Input file section
            VStack {
                HStack {
                    Text("Input Audio File:")
                        .frame(width: 150, alignment: .leading)
                    Text(inputFile?.lastPathComponent ?? "No file selected")
                        .frame(maxWidth: .infinity, alignment: .leading)
                    Button("Browse") {
                        selectAudioFile()
                    }
                    .disabled(isProcessing)
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(5)
            }
            .padding()
            
            // Output file section
            VStack {
                HStack {
                    Text("Output File:")
                        .frame(width: 150, alignment: .leading)
                    Text(outputFile?.lastPathComponent ?? "No file selected")
                        .frame(maxWidth: .infinity, alignment: .leading)
                    Button("Browse") {
                        selectOutputFile()
                    }
                    .disabled(isProcessing)
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(5)
            }
            .padding()
            
            // Settings section
            VStack {
                Text("Noise Reduction Settings")
                    .font(.headline)
                    .padding()
                
                HStack {
                    Text("Noise Sample Duration (sec):")
                        .frame(width: 200, alignment: .leading)
                    Slider(value: $noiseSampleDuration, in: 0.5...10.0, step: 0.5)
                    Text(String(format: "%.1f", noiseSampleDuration))
                        .frame(width: 50, alignment: .trailing)
                }
                .padding()
                
                HStack {
                    Text("Processing Chunk Duration (sec):")
                        .frame(width: 200, alignment: .leading)
                    Slider(value: $chunkDuration, in: 10.0...300.0, step: 10.0)
                    Text(String(format: "%.0f", chunkDuration))
                        .frame(width: 50, alignment: .trailing)
                }
                .padding()
                
                HStack {
                    CheckboxView(label: "Keep original file (don't overwrite)", isChecked: $keepOriginal)
                }
                .padding()
            }
            .padding()
            .background(Color.gray.opacity(0.1))
            .cornerRadius(5)
            
            // Action buttons
            HStack {
                Button(action: {
                    denoiseAudio()
                }) {
                    Text("Apply Noise Reduction")
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .disabled(isProcessing || inputFile == nil || outputFile == nil)
                
                Button(action: {
                    cancelDenoise()
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
                Text("Processing Status")
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
            // Ensure window appears properly
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                if let window = NSApplication.shared.windows.first {
                    window.makeKeyAndOrderFront(nil)
                    NSApplication.shared.activate(ignoringOtherApps: true)
                }
            }
            
            // Check ffmpeg installation
            checkFFmpegInstallation()
        }
    }
    
    func selectAudioFile() {
        let openPanel = NSOpenPanel()
        openPanel.allowedContentTypes = [.audio]
        openPanel.allowsMultipleSelection = false
        
        if openPanel.runModal() == .OK {
            inputFile = openPanel.urls.first
            // Auto-set output path
            if let inputFile = inputFile {
                let dirName = inputFile.deletingLastPathComponent()
                let baseName = inputFile.lastPathComponent
                let nameWithoutExt = baseName.split(separator: ".").dropLast().joined(separator: ".")
                let ext = baseName.split(separator: ".").last.map(String.init) ?? ""
                let outputFileName = "denoised_" + nameWithoutExt + "." + ext
                outputFile = dirName.appendingPathComponent(outputFileName)
            }
        }
    }
    
    func selectOutputFile() {
        let openPanel = NSOpenPanel()
        openPanel.canChooseFiles = true
        openPanel.canChooseDirectories = false
        openPanel.allowsMultipleSelection = false
        openPanel.allowedContentTypes = [.audio]
        
        if let inputFile = inputFile {
            // Set default file name and extension
            let baseName = inputFile.lastPathComponent
            openPanel.nameFieldStringValue = "denoised_" + baseName
        }
        
        if openPanel.runModal() == .OK {
            outputFile = openPanel.urls.first
        }
    }
    
    func denoiseAudio() {
        guard let inputFile = inputFile, let outputFile = outputFile else { return }
        
        isProcessing = true
        statusMessage = "Processing audio..."
        progress = 0.0
        logMessages = []
        
        // Log the start of processing
        logMessage("Starting noise reduction process")
        logMessage("Input file: \(inputFile.lastPathComponent)")
        logMessage("Output file: \(outputFile.lastPathComponent)")
        logMessage("Noise sample duration: \(noiseSampleDuration) seconds")
        logMessage("Chunk duration: \(chunkDuration) seconds")
        
        // Run in a background task to avoid blocking UI
        Task.detached {
            do {
                // Configure Python path
                let sys = Python.import("sys")
                
                // Add the directory containing de_noise.py to Python path
                let pythonScriptPath = "/Users/jk/gits/hub/youtube"
                // Convert String to PythonObject and check if it's in sys.path
                let pythonPathObj = PythonObject(pythonScriptPath)
                if Python.bool(sys.path.__contains__(pythonPathObj)) == false {
                    sys.path.append(pythonPathObj)
                    await MainActor.run {
                        self.logMessage("Added Python script path to sys.path")
                    }
                }
                
                // Import the Python noise reduction module
                let de_noise = Python.import("de_noise")
                
                // Get all UI values within the main actor context
                let (inputFileCopy, outputFileCopy, noiseDurationCopy, chunkDurationCopy) = await Task { @MainActor in
                    return (inputFile, outputFile, noiseSampleDuration, chunkDuration)
                }.value
                
                // Call the Python function for noise reduction with parameters in a detached task
                _ = await Task.detached { () -> PythonObject in
                    let inputPathObj = PythonObject(inputFileCopy.path)
                    let outputPathObj = PythonObject(outputFileCopy.path)
                    let noiseSampleDurationObj = PythonObject(noiseDurationCopy)
                    let chunkDurationObj = PythonObject(chunkDurationCopy)
                    return de_noise.reduce_noise(inputPathObj, outputPathObj, 
                                                noise_sample_duration: noiseSampleDurationObj,
                                                chunk_duration: chunkDurationObj)
                }.value
                
                // Check if any Python exception occurred
                let pythonException = Python.exception()
                if Bool(pythonException) == true {
                    throw NSError(domain: "PythonError", code: 1, userInfo: [NSLocalizedDescriptionKey: String(describing: pythonException)])
                }
                
                // Update UI on main thread
                await MainActor.run {
                    self.logMessage("Noise reduction completed successfully!")
                    self.statusMessage = "Denoising completed successfully!"
                    self.progress = 1.0
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
    
    func cancelDenoise() {
        // In a real application, you would need to properly cancel the Python process
        statusMessage = "Processing cancelled"
        isProcessing = false
        logMessage("Processing cancelled by user")
    }
    
    func logMessage(_ message: String) {
        let timestamp = Date().formatted(date: .omitted, time: .standard)
        logMessages.append("[\(timestamp)] \(message)")
    }
    
    func checkFFmpegInstallation() {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/bin/bash")
        process.arguments = ["-c", "which ffmpeg > /dev/null 2>&1"]
        
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe
        
        do {
            try process.run()
            process.waitUntilExit()
            
            if process.terminationStatus == 0 {
                logMessage("ffmpeg installation detected")
            } else {
                logMessage("Warning: ffmpeg is not detected! Some audio formats may not be supported.")
                logMessage("Please install ffmpeg for best results.")
            }
        } catch {
            logMessage("Error checking ffmpeg: \(error.localizedDescription)")
        }
    }
}

// Custom Checkbox view
struct CheckboxView: View {
    let label: String
    @Binding var isChecked: Bool
    
    var body: some View {
        HStack {
            Button(action: {
                isChecked.toggle()
            }) {
                Image(systemName: isChecked ? "checkmark.square.fill" : "square")
                    .foregroundColor(isChecked ? .blue : .gray)
            }
            Text(label)
        }
    }
}
