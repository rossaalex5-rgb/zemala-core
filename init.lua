-- ZEMALA HMI Spatial State Mod (init.lua)
local http = core.request_http_api()
local timer = 0
local poll_interval = 3.47 -- Der atomare Resonanz-Takt

if not http then
    core.log("error", "[ZEMALA HMI] HTTP API nicht in minetest.conf freigegeben!")
else
    core.log("action", "[ZEMALA HMI] HTTP-Brücke zum Zemala-Core erfolgreich geöffnet.")
end

core.register_globalstep(function(dtime)
    if not http then return end
    timer = timer + dtime
    if timer >= poll_interval then
        timer = 0
        
        -- Asynchroner Abruf der MCP-Ressource ohne Blockade des Render-Threads
        http.fetch({
            url = "http://127.0.0.1:8000/mcp/latest",
            method = "GET",
        }, function(res)
            if res.succeeded and res.code == 200 then
                local data = core.parse_json(res.data)
                if data and data.uri then
                    -- Visuelle Synchronisation im Gitter
                    core.log("action", "[ZEMALA HMI] Zustand im Raum synchronisiert: " .. data.uri)
                end
            else
                core.log("warning", "[ZEMALA HMI] Verbindung zum Edge-Node pausiert.")
            end
        end)
    end
end)
