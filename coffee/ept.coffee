db = $.couch.db "habitat"

flights = {}
payloads = {}

selected_flight = null
selected_payload = null

get_flights = ->
    db.view "flight/launch_time_including_payloads", {
        include_docs: true,
        stale: "update_after",
        descending: true,
        success: (data) ->
            for row in data.rows
                if row['key'][row.key.length - 1] == 0
                    flights[row['id']] = row['doc']
            show_flights()
    }

get_payloads = ->
    db.view "payload_configuration/name_time_created", {
        include_docs: true,
        stale: "update_after",
        success: (data) ->
            for row in data.rows
                payloads[row['id']] = row['doc']
            show_payloads()
    }

show_flights = ->
    to_render = (flight for id, flight of flights when filter_flight flight)
    $('#flight-list').html $('#flight-row-template').render to_render

show_payloads = ->
    to_render = (payld for id, payld of payloads when filter_payload payld)
    $('#payload-list').html $('#payload-row-template').render to_render

filter_flight = (flight) ->
    return filter_thing flight, $('#filter-flights').val()

filter_payload = (payload) ->
    filtered = filter_thing payload, $('#filter-payloads').val()
    if selected_flight
        in_flight = payload['_id'] in flights[selected_flight]['payloads']
    return filtered and (not selected_flight or in_flight)

filter_thing = (thing, str) ->
    return true if not str
    return (thing['name'].toLowerCase().indexOf str.toLowerCase()) != -1

select_flight = ->
    flight_id = $(this).attr 'id'
    $('.flight-row').removeClass('selected-row')
    selected_payload = null
    $('.hide-without-payload').hide()
    if flight_id != selected_flight
        $(this).addClass('selected-row')
        selected_flight = flight_id
        $('#filter-payloads').val("")
        $('#payloads-in').html("in #{flights[flight_id]['name']}")
    else
        selected_flight = null
        $('#payloads-in').html("All")
    show_payloads()

select_payload = ->
    payload_id = $(this).attr 'id'
    $('.payload-row').removeClass('selected-row')
    if payload_id != selected_payload
        $(this).addClass('selected-row')
        selected_payload = payload_id
        $('.hide-without-payload').show()
        render_select_data()
    else
        selected_payload = null
        $('.hide-without-payload').hide()

render_select_data = ->
    intro = "Select data to export from payload "
    intro += payloads[selected_payload]['name']
    if selected_flight
        intro += " (on flight #{flights[selected_flight]['name']}):"
    else
        intro += " (across all flights):"
    $('#select-data-intro').html intro
    fields = [{name: 'raw data'}]
    for sentence in payloads[selected_payload]['sentences']
        for field in sentence['fields']
            if field not in fields
                fields.push {name: field['name']}
    $('#select-data').html $('#data-checkbox-template').render fields
    select_data()

toggle_select_all = ->
    $('.select-data-checkbox').attr 'checked', $(this).prop 'checked'
    select_data()

select_data = ->
    base_url = "/habitat/_design/ept/_list/"
    base_url = "/habitat/_design/ept/_list/"
    if selected_flight
        key = "[\"#{selected_flight}\",\"#{selected_payload}\""
        viewpart = "/payload_telemetry/flight_payload_time"
        querypart = "?include_docs=true&startkey=#{key}]&endkey=#{key},[]]"
    else
        key = "[\"#{selected_payload}\""
        viewpart = "/payload_telemetry/payload_time"
        querypart = "?include_docs=true&startkey=#{key}]&endkey=#{key},[]]"
    fields = $('.select-data-checkbox:checked').map ->
        val = $(this).attr 'value'
        if val == "raw data"
            val = "_sentence"
        return val
    .get().join(",")
    querypart += "&fields=#{fields}"
    $('#export-csv').attr('href', base_url + "csv" + viewpart + querypart)
    $('#export-json').attr('href', base_url + "json" + viewpart + querypart)
    if fields != ""
        $('.hide-without-data').show()
    else
        $('.hide-without-data').hide()

$('.hide-without-payload').hide().css('visibility', 'visible')
$('.hide-without-data').hide().css('visibility', 'visible')
$('#filter-flights').on 'keyup', show_flights
$('#filter-payloads').on 'keyup', show_payloads
$('#flight-list').on 'click', '.flight-row', select_flight
$('#payload-list').on 'click', '.payload-row', select_payload
$('#select-data').on 'change', '.select-data-checkbox', select_data
$('#toggle-select-all').on 'change', toggle_select_all

get_flights()
get_payloads()
