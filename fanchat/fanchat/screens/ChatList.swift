//
//  ChatList.swift
//  fanchat
//
//  Created by Angus Symons on 21/9/2022.
//

import SwiftUI

struct ChatList: View {
    
    @ObservedObject var session = SessionStore()
    @ObservedObject var viewModel = ChatroomsViewModel()
    @State var joinModal = false
    
    init() {
        viewModel.fetchData()
    }
    
    var body: some View {
        NavigationView {
            List(viewModel.chatrooms) { chatroom in
                NavigationLink(destination: Messages(chatroom: chatroom)) {
                    HStack {
                        //                        VStack {
                        Text(chatroom.title)
                        Spacer()
                    }
                }
                .navigationBarTitle("Chatrooms")
                .navigationBarItems(trailing: Button(action: {
                    self.joinModal = true
                }, label: {
                    Image(systemName: "plus.circle")
                }))
                .sheet(isPresented: $joinModal, content: {
                    Join(isOpen: $joinModal)
                })
            }
        }
    }
}

struct ChatList_Previews: PreviewProvider {
    static var previews: some View {
        ChatList()
    }
}
