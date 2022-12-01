//
//  userViewModel.swift
//  fanchat
//
//  Created by Angus Symons on 21/11/2022.
//

import Foundation
import FirebaseFirestore

class MatchViewModel: ObservableObject {
	@Published var matches = [Match]()
	
	private var db = Firestore.firestore()
	
	func fetchData() {
		db.collection("nba_daily_matches").addSnapshotListener { (querySnapshot, error) in
			guard let documents = querySnapshot?.documents else {
				print("No documents")
				return
			}
			
			self.matches = documents.map { queryDocumentSnapshot -> Match in
				let data = queryDocumentSnapshot.data()
				
				let id = data["id"] as? String ?? ""
				let status = data["status"] as? String ?? ""
				let scheduled = data["scheduled"] as? String ?? ""
				let venue_name = data["venue_name"] as? String ?? ""
				let home_name = data["home_name"] as? String ?? ""
				let home_alias = data["home_alias"] as? String ?? ""
				let home_points = data["home_points"] as? String ?? ""
				let away_name = data["away_name"] as? String ?? ""
				let away_alias = data["away_alias"] as? String ?? ""
				let away_points = data["away_points"] as? String ?? ""

				return Match(id: id, status: status, scheduled: scheduled, venue_name: venue_name, home_name: home_name, home_alias: home_alias, home_points: home_points, away_name: away_name, away_alias: away_alias, away_points: away_points)
			}
		}
	}
}
