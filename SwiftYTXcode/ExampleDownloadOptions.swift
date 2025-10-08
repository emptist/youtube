// Example of a standard implementation with row titles
import SwiftUI

struct ExampleDownloadOptions: View {
    // Mock state variables
    @State private var downloadType = DownloadType.audio
    @State private var audioFormat = AudioFormat.m4a
    @State private var isProcessing = false
    @State private var applyNoiseReduction = false
    @State private var keepRawAudio = false
    
    // Enum definitions
    enum DownloadType: String, CaseIterable, Identifiable {
        case audio = "Audio Only"
        case video = "Video + Audio"
        
        var id: String { self.rawValue }
    }
    
    enum AudioFormat: String, CaseIterable, Identifiable {
        case m4a = "M4A"
        case mp3 = "MP3"
        
        var id: String { self.rawValue }
    }
    
    var body: some View {
        VStack {
            Text("Download Options")
                .font(.headline)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.bottom, 5)
            
            // Standard pattern with row titles
            // 1. Using fixed-width labels for alignment
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
            
            // Alternative compact version
            HStack {
                // Noise reduction options with row titles
                VStack(alignment: .leading) {
                    HStack {
                        Text("Apply Noise Reduction:")
                            .font(.system(size: 14))
                        Toggle(isOn: $applyNoiseReduction) {}
                            .disabled(isProcessing || downloadType == .video)
                    }
                    
                    HStack {
                        Text("Keep Raw Audio:")
                            .font(.system(size: 14))
                        Toggle(isOn: $keepRawAudio) {}
                            .disabled(isProcessing || downloadType == .video || !applyNoiseReduction)
                    }
                }
            }
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(5)
    }
}