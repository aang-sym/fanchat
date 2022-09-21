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
                    .padding([.trailing, .leading], 20)
                    .padding([.bottom], 5)
                
                SecureField("Password", text: $password)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding([.bottom, .trailing, .leading], 20)
                
                FullWidthButton(label : "Log in", action: {
                    sessionStore.signIn(email: email, password: password)
                })
                    .padding([.trailing, .leading], 20)
                
                FullWidthButton(label : "Sign Up", action: {
                    sessionStore.signUp(email: email, password: password)
                })
                    .padding([.bottom, .trailing, .leading], 20)
            }
            .navigationTitle("Login")
        }
    }
}

struct Login_Previews: PreviewProvider {
    static var previews: some View {
        Login()
    }
}
