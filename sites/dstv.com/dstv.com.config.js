const axios = require('axios')
const dayjs = require('dayjs')
const utc = require('dayjs/plugin/utc')
const timezone = require('dayjs/plugin/timezone')

dayjs.extend(utc)
dayjs.extend(timezone)

module.exports = {
  site: 'dstv.com',
  request: {
    cache: {
      maxAge: 6 * 60 * 60 * 1000 // 6h
    }
  },
  url: function ({ channel, date }) {
    const [region] = channel.site_id.split('#')
    const packageName = region === 'nga' ? 'DStv%20Premium' : ''

    return `https://www.dstv.com/umbraco/api/TvGuide/GetProgrammes?d=${date.format(
      'YYYY-MM-DD'
    )}&package=${packageName}&country=${region}`
  },
  async parser({ content, channel }) {
    let programs = []
    const items = parseItems(content, channel)
    for (const item of items) {
      const details = await loadProgramDetails(item)
      programs.push({
        title: item.Title,
        description: parseDescription(details),
        icon: parseIcon(details),
        category: parseCategory(details),
        start: parseStart(item),
        stop: parseStop(item)
      })
    }

    return programs
  },
  async channels({ country }) {
    const data = await axios
      .get(
        `https://www.dstv.com/umbraco/api/TvGuide/GetProgrammes?d=2022-03-10&package=DStv%20Premium&country=${country}`
      )
      .then(r => r.data)
      .catch(console.log)

    return data.Channels.map(item => {
      return {
        site_id: `${country}#${item.Number}`,
        name: item.Name
      }
    })
  },
  async rawChannels( country ) {
    const data = await axios
      .get(
        `https://www.dstv.com/umbraco/api/TvGuide/GetChannels?country=${country}&unit=dstv`
      )
      .then(r => r.data)
      .catch(console.log)

    return data.Channels.map(item => {
      return {
        id: item.Number,
        country: country,
        site_id: `${country}#${item.Number}`,
        name: item.Name,
        tag: item.Tag,
        icon: item.Logo
      }
    })
  }
}

function parseDescription(details) {
  return details ? details.Synopsis : null
}

function parseIcon(details) {
  return details ? details.ThumbnailUri : null
}

function parseCategory(details) {
  return details ? details.SubGenres : null
}

async function loadProgramDetails(item) {
  const url = `https://www.dstv.com/umbraco/api/TvGuide/GetProgramme?id=${item.Id}`

  return axios
    .get(url)
    .then(r => r.data)
    .catch(console.error)
}

function parseStart(item) {
  return dayjs.tz(item.StartTime, 'YYYY-MM-DDTHH:mm:ss+02:00', 'Africa/Johannesburg')
}

function parseStop(item) {
  return dayjs.tz(item.EndTime, 'YYYY-MM-DDTHH:mm:ss+02:00', 'Africa/Johannesburg')
}

function parseItems(content, channel) {
  const [_, channelId] = channel.site_id.split('#')
  const data = JSON.parse(content)
  if (!data || !Array.isArray(data.Channels)) return []
  const channelData = data.Channels.find(c => c.Number === channelId)
  if (!channelData || !Array.isArray(channelData.Programmes)) return []

  return channelData.Programmes
}
