//
//  fanchatApp.swift
//  fanchat
//
//  Created by Angus Symons on 21/9/2022.
//

import SwiftUI
import Firebase

@main
struct fanchatApp: App {
    
    init() {
        FirebaseApp.configure()
    }
    
    var body: some Scene {
        WindowGroup {
            LoginView()
        }
    }
}
