//
//  Contact.swift
//  hackmit-2019-app
//
//  Created by Katherine Xiao on 9/14/19.
//  Copyright © 2019 Elizabeth Zhou. All rights reserved.
//

import Foundation

struct Contact: Hashable, Codable {
    var id: Int
    var firstName: String
    var lastName: String
    fileprivate var imageName: String
    
}
