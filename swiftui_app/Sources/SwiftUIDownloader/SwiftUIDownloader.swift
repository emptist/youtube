import SwiftUI
import AppKit

@main
struct TestApp: App {
    init() {
        // Configure application settings
        NSApplication.shared.setActivationPolicy(.regular)
        print("TestApp initialized")
    }
    
    var body: some Scene {
        WindowGroup("Test Window App") {
            ContentView()
                .frame(minWidth: 400, minHeight: 300)
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
    @State private var text: String = ""
    @State private var message: String = ""
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Test Window App")
                .font(.largeTitle)
                .fontWeight(.bold)
                
            TextField("Enter some text", text: $text)
                .textFieldStyle(.roundedBorder)
                .padding()
                
            Button(action: {
                message = "You entered: \(text.isEmpty ? "nothing" : text)"
            }) {
                Text("Show Text")
                    .font(.headline)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(10)
            }
            
            Text(message)
                .padding()
        }
        .padding()
        .frame(minWidth: 600, minHeight: 400)
        .onAppear {
            print("ContentView appeared on screen")
            // Ensure the window is frontmost and focused
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                if let window = NSApp.windows.first {
                    window.makeKeyAndOrderFront(nil)
                    NSApp.activate(ignoringOtherApps: true)
                }
            }
        }
    }
}
