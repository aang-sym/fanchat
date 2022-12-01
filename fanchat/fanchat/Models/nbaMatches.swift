//
//  nbaMatches.swift
//  fanchat
//
//  Created by Angus Symons on 21/11/2022.
//

import Foundation

struct Match: Identifiable {
	var id: String
	var status: String
	var scheduled: String
	var venue_name: String
	var home_name: String
	var home_alias: String
	var home_points: String
	var away_name: String
	var away_alias: String
	var away_points: String
}
