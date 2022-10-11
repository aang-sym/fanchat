//
//  MainMessagesView.swift
//  fanchat
//
//  Created by Angus Symons on 11/10/2022.
//

import SwiftUI

struct MainMessagesView: View {

    @State var shouldShowLogOutOptions = false

    private var customNavBar: some View {
        HStack(spacing: 16) {

            VStack(alignment: .leading, spacing: 4) {
                Text("USERNAME")
                    .font(.system(size: 24, weight: .bold))

                HStack {
                    Circle()
                        .foregroundColor(.green)
                        .frame(width: 14, height: 14)
                    Text("online")
                        .font(.system(size: 12))
                        .foregroundColor(Color(.lightGray))
                }

            }

            Spacer()
            Button {
                shouldShowLogOutOptions.toggle()
            } label: {
                Image(systemName: "gear")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(Color(.label))
            }
        }
        .padding()
        .actionSheet(isPresented: $shouldShowLogOutOptions) {
            .init(title: Text("Settings"), message: Text("What do you want to do?"), buttons: [
                .destructive(Text("Sign Out"), action: {
                    print("handle sign out")
                }),
                    .cancel()
            ])
        }
    }

    var body: some View {
        NavigationView {
            
            VStack {
                customNavBar
                sportSelectView
                liveMatchesView
            }
            .overlay(
                newMessageButton, alignment: .bottom)
            .navigationBarHidden(true)
            .background(Color("pageBackground"))
        }
    }
    
    private var sportSelectView: some View{
        ScrollView(.horizontal) {
            HStack(spacing: 20) {
                ForEach(0..<10, id: \.self) { num in
                    HStack {
                        HStack {
                            Image(systemName: "football")
                                .foregroundColor(.black)
                                .font(.system(size: 32))
                                .padding(8)
                                .frame(width: 25, height: 10)
                            
                            VStack {
                                Text("AFL")
                                    .font(.system(size: 15, weight: .bold))
                            }
                        }   .padding()
                            .background(
                                RoundedRectangle(cornerRadius: 50, style: .continuous).fill(Color.blue)
                            )
                            .overlay(
                                RoundedRectangle(cornerRadius: 50, style: .continuous)
                                    .stroke(Color.blue, lineWidth: 1)
                            )
                    }
                }
            }.padding(10)
        }
        
        }
    
    private var liveMatchesView: some View {
        ScrollView {
            ForEach(0..<5, id: \.self) { num in
                VStack {
                    HStack(spacing: 16) {
                        VStack(alignment: .leading) {
                            Image("afl_collingwood")
                                .resizable()
                                .scaledToFit()
                                .frame(width:70, height:80)
                                .font(.system(size: 32))
                                .padding(.leading, 25)
                            
                            Text("Collingwood")
                                .font(.system(size: 10, weight: .semibold))
                                .foregroundColor(Color(.black))
                                .multilineTextAlignment(.center)
                                .padding(.leading, 30)
                        }
                        Spacer()

                        VStack(alignment: .center) {
                            Text("MCG")
                                .font(.system(size: 18, weight: .bold))
                                .fontWeight(.semibold)
                            Text("Round 2")
                                .font(.system(size: 14))
                                .foregroundColor(Color(.lightGray))
                            Text("67 - 53")
                                .font(.system(size: 25, weight: .bold))
                                .foregroundColor(Color(.black))
                        }
                        Spacer()
                        
                        VStack(alignment: .leading) {
                            Image("afl_geelong")
                                .resizable()
                                .scaledToFit()
                                .frame(width:70, height:80)
                                .font(.system(size: 32))
                            
                            Text("Geelong")
                                .font(.system(size: 10, weight: .semibold))
                                .foregroundColor(Color(.black))
                                .multilineTextAlignment(.center)
                                
                        }.padding(.trailing, 25)
                        .padding(.vertical, 25)
                    }.background(
                        RoundedRectangle(cornerRadius: 15, style: .continuous).fill(Color.white.shadow(.drop(color: .gray, radius: 2, x: 0, y: 3)))
                    ) .padding(.vertical, 8)
                }     .padding(.horizontal)

            }.padding(.bottom, 50)
        }
    }

    private var newMessageButton: some View {
        Button {

        } label: {
            HStack {
                Spacer()
                Text("+ New Message")
                    .font(.system(size: 16, weight: .bold))
                Spacer()
            }
            .foregroundColor(.white)
            .padding(.vertical)
                .background(Color.blue)
                .cornerRadius(32)
                .padding(.horizontal)
                .shadow(radius: 15)
        }
    }
}

struct MainMessagesView_Previews: PreviewProvider {
    static var previews: some View {
        MainMessagesView()
    }
}
