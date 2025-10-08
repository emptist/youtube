// swift-tools-version: 6.2

import SwiftUI
import PythonKit
import AppKit

@main
struct SwiftDenoiserXcode: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var delegate
    
    var body: some Scene {
        WindowGroup {
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
    @State private var outputPath: URL?
    @State private var statusMessage = "Select an audio file to denoise"
    @State private var isProcessing = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Audio Denoiser")
                .font(.title)
                .bold()
            
            HStack {
                Button("Select File") {
                    selectAudioFile()
                }
                .disabled(isProcessing)
                
                Text(inputFile?.lastPathComponent ?? "No file selected")
                    .foregroundColor(inputFile != nil ? .primary : .secondary)
            }
            
            HStack {
                Button("Select Output Folder") {
                    selectOutputFolder()
                }
                .disabled(isProcessing)
                
                Text(outputPath?.lastPathComponent ?? "No folder selected")
                    .foregroundColor(outputPath != nil ? .primary : .secondary)
            }
            
            Button("Denoise") {
                denoiseAudio()
            }
            .disabled(isProcessing || inputFile == nil || outputPath == nil)
            .buttonStyle(.borderedProminent)
            
            Text(statusMessage)
                .foregroundColor(isProcessing ? .blue : .black)
        }
        .padding()
        .frame(minWidth: 600, minHeight: 400)
        .onAppear {
            // Ensure window appears properly
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                if let window = NSApplication.shared.windows.first {
                    window.makeKeyAndOrderFront(nil)
                    NSApplication.shared.activate(ignoringOtherApps: true)
                }
            }
        }
    }
    
    func selectAudioFile() {
        let openPanel = NSOpenPanel()
        openPanel.allowedContentTypes = [.audio]
        openPanel.allowsMultipleSelection = false
        
        if openPanel.runModal() == .OK {
            inputFile = openPanel.urls.first
        }
    }
    
    func selectOutputFolder() {
        let openPanel = NSOpenPanel()
        openPanel.canChooseDirectories = true
        openPanel.canChooseFiles = false
        openPanel.allowsMultipleSelection = false
        
        if openPanel.runModal() == .OK {
            outputPath = openPanel.urls.first
        }
    }
    
    func denoiseAudio() {
        guard let inputFile = inputFile, let outputPath = outputPath else { return }
        
        isProcessing = true
        statusMessage = "Processing audio..."
        
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
                }
                
                // Import the Python noise reduction module
                let de_noise = Python.import("de_noise")
                
                // Prepare output file path
                let inputFilename = inputFile.lastPathComponent
                let outputFilename = "denoised_" + inputFilename
                let outputFile = outputPath.appendingPathComponent(outputFilename)
                
                // Call the Python function for noise reduction
                let inputPathObj = PythonObject(inputFile.path)
                let outputPathObj = PythonObject(outputFile.path)
                _ = de_noise.reduce_noise(inputPathObj, outputPathObj)
                
                // Check if any Python exception occurred
                let pythonException = Python.exception()
                if Bool(pythonException) == true {
                    throw NSError(domain: "PythonError", code: 1, userInfo: [NSLocalizedDescriptionKey: String(describing: pythonException)])
                }
                
                // Update UI on main thread
                await MainActor.run {
                    statusMessage = "Denoising completed successfully!"
                    isProcessing = false
                }
            } catch {
                // Handle errors
                await MainActor.run {
                    statusMessage = "Error: \(error.localizedDescription)"
                    isProcessing = false
                }
            }
        }
    }
}
