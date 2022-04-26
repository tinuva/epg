const _ = require('lodash')
const file = require('./file')

const DATA_DIR = process.env.DATA_DIR || './scripts/data'

class API {
  constructor(filepath) {
    console.log(`constructor: Filepath ${filepath}`)
    this.filepath = file.resolve(filepath)
    console.log(`constructor: This Filepath ${this.filepath}`)
  }

  async load() {
    console.log(`load: This Filepath ${this.filepath}`)
    const data = await file.read(this.filepath)
    console.log(`load: data `)
    console.log(data)

    this.collection = JSON.parse(data)
  }

  find(query) {
    return _.find(this.collection, query)
  }

  all() {
    return this.collection
  }
}

const api = {}

api.channels = new API(`${DATA_DIR}/channels.json`)
api.countries = new API(`${DATA_DIR}/countries.json`)
api.subdivisions = new API(`${DATA_DIR}/subdivisions.json`)

module.exports = api
