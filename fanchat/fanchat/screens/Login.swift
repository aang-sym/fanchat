//
//  Login.swift
//  fanchat
//
//  Created by Angus Symons on 21/9/2022.
//

import SwiftUI

struct Login: View {
    @State var email = ""
    @State var password = ""
    @ObservedObject var sessionStore = SessionStore()
    
    var body: some View {
        NavigationView {
            VStack {
                TextField("Email", text: $email)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                
                SecureField("Password", text: $password)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                
                FullWidthButton(label : "Log in", action: {
                    sessionStore.signIn(email: email, password: password)
                })
                
                FullWidthButton(label : "Log in", action: {
                    sessionStore.signUp(email: email, password: password)
                })
            }
            .navigationBarTitle("Login")
        }
    }
}

struct Login_Previews: PreviewProvider {
    static var previews: some View {
        Login()
    }
}
