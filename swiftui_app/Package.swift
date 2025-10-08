// swift-tools-version: 6.2
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "SwiftUIDownloader",
    platforms: [
        .macOS(.v11)
    ],
    dependencies: [
        // PythonKit for Python integration
        .package(url: "https://github.com/pvieito/PythonKit.git", from: "0.5.0")
    ],
    targets: [
        // Targets are the basic building blocks of a package, defining a module or a test suite.
        // Targets can depend on other targets in this package and products from dependencies.
        .executableTarget(
            name: "SwiftUIDownloader",
            dependencies: [
                .product(name: "PythonKit", package: "PythonKit")
            ]
        ),
    ]
)
