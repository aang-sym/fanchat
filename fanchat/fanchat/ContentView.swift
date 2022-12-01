//
//  ContentView.swift
//  fanchat
//
//  Created by Angus Symons on 14/10/2022.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
			TabView{
//				LoginView()
//					.tabItem{
//						Image(systemName: "chevron.forward.circle.fill")
//						Text("Sign In")
//					}
				MainMessagesView()
					.tabItem{
						Image(systemName: "house")
						Text("Home")
					}
			}
    }
}

//struct ContentView: View {
//	@ObservedObject private var viewModel = MatchViewModel()
//
//	var body: some View {
//		NavigationView {
//			List(viewModel.matches) { match in
//				VStack(alignment: .leading) {
//					Text(match.home_name)
//						.font(.title)
//					Text(match.away_name)
//						.font(.subheadline)
//				}
//			}
//			.navigationBarTitle("Matches")
//			.onAppear() {
//				self.viewModel.fetchData()
//				}
//		}
//	}
//}

struct ContentView_Previews: PreviewProvider {
	static var previews: some View {
		ContentView()
	}
}
