//
//  FullWidthButton.swift
//  fanchat
//
//  Created by Angus Symons on 21/9/2022.
//

import SwiftUI

struct FullWidthButton: View {
    let label: String
    let action: () -> Void
    
    var body: some View {
        Button(action: {
            action()
        }) {
            ZStack {
                Rectangle()
                    .foregroundColor(/*@START_MENU_TOKEN@*/.blue/*@END_MENU_TOKEN@*/)
                    .frame(height: 45)
                    .cornerRadius(8.0)
                Text(label)
                    .foregroundColor(.white)
                    .fontWeight(.semibold)
            }
        }
    }
}

struct FullWidthButton_Previews: PreviewProvider {
    static var previews: some View {
        FullWidthButton(label: "Test Button", action: {
            print("button pressed!")
        })
    }
}
