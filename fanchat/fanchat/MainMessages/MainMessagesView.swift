//
//  MainMessagesView.swift
//  fanchat
//
//  Created by Angus Symons on 11/10/2022.
//

import SwiftUI
import Foundation
import FirebaseFirestore

extension View {
	func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View {
		clipShape( RoundedCorner(radius: radius, corners: corners) )
	}
}

struct RoundedCorner: Shape {
	
	var radius: CGFloat = .infinity
	var corners: UIRectCorner = .allCorners
	
	func path(in rect: CGRect) -> Path {
		let path = UIBezierPath(roundedRect: rect, byRoundingCorners: corners, cornerRadii: CGSize(width: radius, height: radius))
		return Path(path.cgPath)
	}
}

struct sportSelectView: View {
	var league: String
	var leagueImage: String
	
	var body: some View {
		ScrollView(.horizontal) {
			HStack {
				ForEach(0..<5, id: \.self) { num in
					HStack {
						HStack {
							Image(leagueImage)
								.resizable()
								.scaledToFit()
								.frame(width: 40)
							
							VStack {
								Text(league)
									.font(.system(size: 15, weight: .bold))
									.foregroundColor(Color(.white))
								
							}
						}   .padding()
							.background(
								RoundedRectangle(cornerRadius: 50, style: .continuous).fill(Color.blue).frame(height: 30)
								
							)
					}
				}
			}.padding(.leading, 10)
		}
	}
}

struct teamView: View {
	@State var isExpanded = false
	var team: String
	var teamImage: String
	
	var body: some View {
		VStack {
			if isExpanded {
				Image(teamImage)
					.resizable()
					.scaledToFit()
					.frame(width:90, height:90)
					.padding(.top)
			} else {
				Image(teamImage)
					.resizable()
					.scaledToFit()
					.frame(width:60, height:60)
			}
			if isExpanded {
				Text(team)
					.font(.system(size: 10, weight: .semibold))
					.foregroundColor(Color(.black))
					.multilineTextAlignment(.center)
					.padding(.bottom)
			}
		}.frame(minWidth: 0, maxWidth: .infinity)
	}
}

struct matchDetailsView: View {
	var arena: String
	var round: String
	var homeScore: String
	var awayScore: String
	var liveTime: String
	@State var isExpanded = false
	
	var body: some View {
		VStack(alignment: .center) {
			if isExpanded {
				Text(arena)
					.font(.system(size: 18, weight: .bold))
					.fontWeight(.semibold)
					.padding(.top)
				Text(round)
					.font(.system(size: 14))
					.foregroundColor(Color(.lightGray))
					.padding(.bottom, -15)
			}
			Text("\(homeScore) - \(awayScore)")
				.font(.system(size: 26, weight: .bold))
				.foregroundColor(Color(.black))
				.padding(.top)
				.padding(.bottom, 0.1)
			Text(liveTime)
				.frame(width: 90, height: 23)
				.font(.system(size: 13, weight: .bold))
				.foregroundColor(Color("timer"))
				.background(
					RoundedRectangle(cornerRadius: 50, style: .continuous)
						.fill(Color("timerBackground"))
					
				)
				.overlay(
					RoundedRectangle(cornerRadius: 50, style: .continuous)
						.stroke(Color("timer"), lineWidth: 2)
				).padding(.bottom)
				.padding(.top, 0.1)
		}.frame(minWidth: 0, maxWidth: .infinity)
	}
}

struct matchExpandedView: View {
	var body: some View {
		VStack {
			Button(action: {
				accessChat()
			}) {
				Label("Chat", systemImage: "message")
			}
		}.padding(.bottom)
	}
	
	func accessChat() {}
}

struct liveMatchView: View {
	@State var isExpanded = true
	
	var body: some View {
		HStack(spacing: 16) {
			if isExpanded {
				VStack{
					HStack {
						teamView(isExpanded: true, team: "Collingwood Magpies", teamImage: "afl_collingwood")
							.padding(.leading)
						Spacer()
						
						matchDetailsView(arena: "MCG", round: "Round 2", homeScore: "112", awayScore: "107", liveTime: "Q4 21:05", isExpanded: true)
						Spacer()
						
						teamView(isExpanded: true, team: "Geelong Cats", teamImage: "afl_geelong")
							.padding(.trailing)
					}
				}
			} else {
				teamView(isExpanded: false, team: "Collingwood Magpies", teamImage: "afl_collingwood")
					.padding(.leading)
				Spacer()
				
				matchDetailsView(arena: "MCG", round: "Round 2", homeScore: "67", awayScore: "53", liveTime: "Q3 21:05", isExpanded: false)
				Spacer()
				
				teamView(isExpanded: false, team: "Geelong Cats", teamImage: "afl_geelong")
					.padding(.trailing)
			}
		}.padding(.vertical, 5)
			.background(
				RoundedRectangle(
					cornerRadius: 15,
					style: .continuous)
				.fill(Color.white
					.shadow(.drop(color: .gray, radius: 2, x: 0, y: 3)))
				.transition(.scale)
				.onTapGesture {
					withAnimation{
						isExpanded.toggle()
					}
				}
			).padding(.vertical, 5)
	}
}

struct teamView2: View {
	var team: String
	var teamImage: String
	var teamStanding: String
	
	var body: some View {
		VStack {
			Image(teamImage)
				.resizable()
				.scaledToFit()
				.frame(width:50, height:50)
			Group {
				Text(teamStanding)
					.font(.system(size: 10, weight: .regular))
					.foregroundColor(Color(.gray)) +
				Text(" ") +
				Text(team)
					.font(.system(size: 10, weight: .regular))
					.foregroundColor(Color(.black))
			}.padding(.top, -10)
		}
	}
}

struct matchDetailsView2: View {
	var homeScore: String
	var awayScore: String
	var period: String
	var liveTime: String
	
	var body: some View {
		HStack(alignment: .center) {
			Text("\(homeScore)")
				.font(.system(size: 30, weight: .regular))
				.foregroundColor(Color(.black))
				.frame(alignment: .leading)
			VStack {
				HStack {
					Image(systemName: "circle.fill")
						.foregroundColor(Color.red)
						.font(.system(size: 5))
						.padding(.trailing, -4)
					Text(period)
						.font(.system(size: 12, weight: .semibold))
				}
				Text(liveTime)
					.font(.system(size: 12, weight: .regular))
			}				.frame(alignment: .center)
				.padding(.horizontal, 7)
			Text("\(awayScore)")
				.font(.system(size: 30, weight: .regular))
				.foregroundColor(Color(.black))
				.frame(alignment: .trailing)
		}
	}
}

struct liveMatchView2: View {
	var homeName: String
	var awayName: String
	var homeScore: String
	var awayScore: String
	var homeLogo: String
	var awayLogo: String
	var venueName: String
	
	var body: some View {
		HStack(spacing: 16) {
			VStack{
				HStack{
					teamView2(team: homeName, teamImage: homeLogo, teamStanding: "4")
						.padding(.leading, 25)
						.padding(.top, 15)
						.padding(.bottom, 10)
					Spacer()
					
					matchDetailsView2(homeScore: homeScore, awayScore: awayScore, period: "Q4", liveTime: "1:05")
					Spacer()
					
					teamView2(team: awayName, teamImage: awayLogo, teamStanding: "1")
						.padding(.trailing, 25)
						.padding(.top, 15)
						.padding(.bottom, 10)
				}
				HStack {
					VStack{
						Image("tnt_logo")
							.resizable()
							.scaledToFit()
							.frame(width: 30)
					}.padding(.leading, 32.5)
					Spacer()
					VStack{
						Text(venueName)
							.font(.system(size: 12, weight: .regular))
						//													Text("Preliminary Final")
						//														.font(.system(size: 12, weight: .regular))
						//														.foregroundColor(Color(.darkGray))
					}
					Spacer()
					VStack{
						Image("nba_logo")
							.resizable()
							.scaledToFit()
							.frame(width: 40, height: 35)
					}.padding(.trailing, 32.5)
						.padding(.vertical)
				}.padding(.top, -27.5)
					.padding(.bottom, 2.5)
					.background(
						Rectangle()
							.fill(Color.gray)
							.opacity(0.1)
							.frame(height: 75)
					)
			}
		}
		.background(
			RoundedRectangle(
				cornerRadius: 15,
				style: .continuous)
			.fill(Color.white
				.shadow(.drop(color: .gray, radius: 2, x: 0, y: 3)))
		)			.mask(
			RoundedRectangle(
				cornerRadius: 15,
				style: .continuous)
			.padding(.vertical, 5)
		)
	}
}

struct liveMatchesView: View {
	@ObservedObject private var viewModel = MatchViewModel()
	
	var body: some View {
		ScrollView {
			ForEach(viewModel.matches) { match in
				let homeName = match.home_name.components(separatedBy: " ")
				let awayName = match.away_name.components(separatedBy: " ")
				let homeLogo = "\(match.home_alias)_logo"
				let awayLogo = "\(match.away_alias)_logo"
				
				VStack {
					liveMatchView2(homeName: homeName[1], awayName: awayName[1], homeScore: match.home_points, awayScore: match.away_points, homeLogo: homeLogo, awayLogo: awayLogo, venueName: match.venue_name)
				}.padding(.horizontal, 10)
			}
			.onAppear() {
				self.viewModel.fetchData()
			}
		}
	}
}

struct settingsButton: View {
	@State var shouldShowLogOutOptions = false
	
	var body: some View {
		Menu {
			Button(action: {
				hideMatches()
			}) {
				Label("Completed matches", systemImage: "eye.slash")
			}
			Button(action: {
				signOut()
			}) {
				Label("Sign out", systemImage: "rectangle.portrait.and.arrow.right")
			}
		} label: {
			Label("", systemImage: "ellipsis")
				.font(.system(size: 24, weight: .bold))
				.foregroundColor(Color(.label))
		}
	}
	
	func signOut() {}
	func hideMatches() {}
}

struct customNavBar: View {
	var body: some View {
		HStack {
			VStack(alignment: .leading) {
				Text("fanchat")
					.font(.system(size: 24, weight: .bold))
			}
			Spacer()
			settingsButton()
		}
		.padding()
	}
}

struct MainMessagesView: View {
	
	var body: some View {
		NavigationView {
			
			VStack {
				sportSelectView(league: "AFL", leagueImage: "afl_logo")
				liveMatchesView()
			}
			.navigationTitle("fanchat")
			.navigationBarTitleDisplayMode(.inline)
			.toolbar {
				ToolbarItemGroup(placement: .navigationBarTrailing) {
					settingsButton()
				}
			}
			.background(Color.gray)
		}
	}
}

struct MainMessagesView_Previews: PreviewProvider {
	static var previews: some View {
		MainMessagesView()
	}
}
