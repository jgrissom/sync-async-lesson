// ============================================================
// Reaction-Game Scoreboard API (cloud edition)
// Python IoT on the TinyPICO : Session 4 (Wi-Fi & IoT)
//
// Drop-in replacement for sessions/04-wifi-iot/code/
// scoreboard_server.py, hosted on Azure App Service. The JSON
// contract (routes, shapes, key spellings, status codes) must
// stay identical to the stdlib server so the boards can switch
// hosts by changing SCOREBOARD_HOST alone.
//
//   POST /result           record a round   (boards, plain http)
//   GET  /scores           all benches + totals
//   GET  /scores/{bench}   one bench
//   GET  /reset?key=...    wipe scores (requires RESET_KEY config)
//   /scalar                interactive API docs
//   /app/                  React leaderboard (wwwroot/app)
//   /classic/              original static leaderboard page
// ============================================================

using System.Text.Json.Nodes;
using System.Text.Json.Serialization;
using Microsoft.Data.Sqlite;
using Scalar.AspNetCore;

const string PlayerBlue = "Blue";
const string PlayerYellow = "Yellow";
string[] players = [PlayerBlue, PlayerYellow];
string[] results = ["win", "false_start"];

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddOpenApi();

var app = builder.Build();

var dbPath = app.Configuration["SCOREBOARD_DB_PATH"]
             ?? Path.Combine(app.Environment.ContentRootPath, "scoreboard.db");
var connectionString = new SqliteConnectionStringBuilder { DataSource = dbPath }.ToString();

using (var conn = new SqliteConnection(connectionString))
{
    conn.Open();
    var create = conn.CreateCommand();
    create.CommandText = """
        CREATE TABLE IF NOT EXISTS scores (
            bench        TEXT    NOT NULL,
            player       TEXT    NOT NULL,
            wins         INTEGER NOT NULL DEFAULT 0,
            false_starts INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (bench, player)
        );
        CREATE TABLE IF NOT EXISTS bench_names (
            bench TEXT PRIMARY KEY,
            name  TEXT NOT NULL
        );
        CREATE UNIQUE INDEX IF NOT EXISTS ux_bench_names_name
            ON bench_names (name COLLATE NOCASE);
        """;
    create.ExecuteNonQuery();
}

// Benches in first-seen order (ORDER BY rowid), players Blue-then-Yellow
// within a bench — matches the stdlib server's dict insertion order.
Dictionary<string, Dictionary<string, PlayerScore>> LoadBenches()
{
    var benches = new Dictionary<string, Dictionary<string, PlayerScore>>();
    using var conn = new SqliteConnection(connectionString);
    conn.Open();
    var cmd = conn.CreateCommand();
    cmd.CommandText = "SELECT bench, player, wins, false_starts FROM scores ORDER BY rowid";
    using var reader = cmd.ExecuteReader();
    while (reader.Read())
    {
        var bench = reader.GetString(0);
        if (!benches.TryGetValue(bench, out var entry))
            benches[bench] = entry = [];
        entry[reader.GetString(1)] = new PlayerScore(reader.GetInt32(2), reader.GetInt32(3));
    }
    return benches;
}

Dictionary<string, string> LoadNames()
{
    var names = new Dictionary<string, string>();
    using var conn = new SqliteConnection(connectionString);
    conn.Open();
    var cmd = conn.CreateCommand();
    cmd.CommandText = "SELECT bench, name FROM bench_names ORDER BY rowid";
    using var reader = cmd.ExecuteReader();
    while (reader.Read())
        names[reader.GetString(0)] = reader.GetString(1);
    return names;
}

Dictionary<string, PlayerScore> Totals(Dictionary<string, Dictionary<string, PlayerScore>> benches)
{
    var totals = players.ToDictionary(p => p, _ => new PlayerScore(0, 0));
    foreach (var entry in benches.Values)
        foreach (var p in players)
            if (entry.TryGetValue(p, out var s))
                totals[p] = new PlayerScore(totals[p].Wins + s.Wins,
                                            totals[p].FalseStarts + s.FalseStarts);
    return totals;
}

// Static files must run BEFORE routing selects an endpoint — otherwise the
// JSON-404 fallback endpoint wins and the static middleware steps aside.
app.UseDefaultFiles();   // "/app/" -> app/index.html, "/classic/" -> classic/index.html
app.UseStaticFiles();
app.UseRouting();

app.MapPost("/result", async (HttpRequest request) =>
{
    string bench, player, result;
    try
    {
        var payload = await JsonNode.ParseAsync(request.Body)
                      ?? throw new FormatException("empty body");
        bench = (payload["bench"] ?? throw new FormatException("'bench'")).ToString();
        player = (payload["player"] ?? throw new FormatException("'player'")).ToString();
        result = (payload["result"] ?? throw new FormatException("'result'")).ToString();
        if (!players.Contains(player) || !results.Contains(result))
            throw new FormatException("bad player or result");
    }
    catch (Exception exc) when (exc is FormatException or System.Text.Json.JsonException)
    {
        return Results.Json(new ErrorBody($"bad request: {exc.Message}"), statusCode: 400);
    }

    using var conn = new SqliteConnection(connectionString);
    conn.Open();
    using var tx = conn.BeginTransaction();
    var ensure = conn.CreateCommand();
    ensure.Transaction = tx;
    ensure.CommandText = """
        INSERT OR IGNORE INTO scores (bench, player) VALUES ($bench, 'Blue');
        INSERT OR IGNORE INTO scores (bench, player) VALUES ($bench, 'Yellow');
        """;
    ensure.Parameters.AddWithValue("$bench", bench);
    ensure.ExecuteNonQuery();

    var column = result == "win" ? "wins" : "false_starts";
    var bump = conn.CreateCommand();
    bump.Transaction = tx;
    bump.CommandText =
        $"UPDATE scores SET {column} = {column} + 1 WHERE bench = $bench AND player = $player";
    bump.Parameters.AddWithValue("$bench", bench);
    bump.Parameters.AddWithValue("$player", player);
    bump.ExecuteNonQuery();
    tx.Commit();

    Console.WriteLine($"  bench {bench} : {player} {result}");
    return Results.Json(LoadBenches()[bench]);
})
.WithSummary("Record a round result")
.WithDescription("""
    Boards POST one of:
      {"bench": "3", "player": "Blue", "result": "win"}
      {"bench": "3", "player": "Yellow", "result": "false_start"}
    Returns the updated entry for that bench. 400 on a malformed body,
    unknown player, or unknown result.
    """)
.Produces<Dictionary<string, PlayerScore>>()
.Produces<ErrorBody>(StatusCodes.Status400BadRequest);

app.MapGet("/scores", () =>
{
    var benches = LoadBenches();
    return Results.Json(new ScoresBody(benches, Totals(benches), LoadNames()));
})
.WithSummary("All benches + class totals")
.WithDescription("""
    Boards call this between rounds; the leaderboard pages poll it every
    1.5 s. Shape: {"benches": {"3": {"Blue": {"wins": 1, "false_starts": 0},
    ...}, ...}, "totals": {"Blue": {...}, "Yellow": {...}},
    "names": {"3": "Jeff's Sweet Game", ...}}. The "names" key is additive
    relative to the classroom stdlib server — boards and the classic page
    ignore it.
    """)
.Produces<ScoresBody>();

app.MapPost("/register", async (HttpRequest request) =>
{
    const int MaxName = 40;
    string bench, name;
    try
    {
        var payload = await JsonNode.ParseAsync(request.Body)
                      ?? throw new FormatException("empty body");
        bench = (payload["bench"] ?? throw new FormatException("'bench'")).ToString();
        name = (payload["name"] ?? throw new FormatException("'name'")).ToString().Trim();
        if (name.Length == 0)
            throw new FormatException("name is empty");
        if (name.Length > MaxName)
            throw new FormatException($"name too long (max {MaxName} chars)");
    }
    catch (Exception exc) when (exc is FormatException or System.Text.Json.JsonException)
    {
        return Results.Json(new ErrorBody($"bad request: {exc.Message}"), statusCode: 400);
    }

    using var conn = new SqliteConnection(connectionString);
    conn.Open();
    using var tx = conn.BeginTransaction();

    // Names are unique class-wide (case-insensitive). A bench re-sending
    // its own name is a rename-to-self, not a conflict.
    var holder = conn.CreateCommand();
    holder.Transaction = tx;
    holder.CommandText = """
        SELECT bench FROM bench_names
        WHERE name = $name COLLATE NOCASE AND bench <> $bench LIMIT 1
        """;
    holder.Parameters.AddWithValue("$bench", bench);
    holder.Parameters.AddWithValue("$name", name);
    if (holder.ExecuteScalar() is string taken)
        return Results.Json(new ErrorBody($"name already taken by bench {taken}"),
                            statusCode: 409);

    // Make the bench visible on the leaderboard immediately (zero scores),
    // so a freshly named game shows up within one poll.
    var ensure = conn.CreateCommand();
    ensure.Transaction = tx;
    ensure.CommandText = """
        INSERT OR IGNORE INTO scores (bench, player) VALUES ($bench, 'Blue');
        INSERT OR IGNORE INTO scores (bench, player) VALUES ($bench, 'Yellow');
        INSERT INTO bench_names (bench, name) VALUES ($bench, $name)
            ON CONFLICT(bench) DO UPDATE SET name = excluded.name;
        """;
    ensure.Parameters.AddWithValue("$bench", bench);
    ensure.Parameters.AddWithValue("$name", name);
    try
    {
        ensure.ExecuteNonQuery();
        tx.Commit();
    }
    catch (SqliteException)
    {
        // Unique-index backstop for two benches racing for the same name.
        return Results.Json(new ErrorBody("name already taken"), statusCode: 409);
    }

    Console.WriteLine($"  bench {bench} registered as \"{name}\"");
    return Results.Json(new OkBody(true, $"bench {bench} registered as \"{name}\""));
})
.WithSummary("Name your game")
.WithDescription("""
    Give your bench's game a title for the leaderboard, e.g.
    {"bench": "3", "name": "Jeff's Sweet Game"}. Registering is optional —
    unnamed benches show as "Bench 3". Re-register any time to rename.
    Max 40 characters. Names are unique class-wide (case-insensitive):
    if another bench already has the name you get 409 Conflict — pick a
    better one.
    """)
.Produces<OkBody>()
.Produces<ErrorBody>(StatusCodes.Status400BadRequest)
.Produces<ErrorBody>(StatusCodes.Status409Conflict);

app.MapGet("/scores/{bench}", (string bench) =>
{
    var benches = LoadBenches();
    return benches.TryGetValue(bench, out var entry)
        ? Results.Json(entry)
        : Results.Json(new ErrorBody($"unknown bench {bench}"), statusCode: 404);
})
.WithSummary("One bench's scores")
.Produces<Dictionary<string, PlayerScore>>()
.Produces<ErrorBody>(StatusCodes.Status404NotFound);

app.MapGet("/reset", (string? key, IConfiguration config) =>
{
    var resetKey = config["RESET_KEY"];
    if (string.IsNullOrEmpty(resetKey))
        return Results.Json(new ErrorBody("reset disabled: no RESET_KEY configured"),
                            statusCode: 403);
    if (key != resetKey)
        return Results.Json(new ErrorBody("bad key"), statusCode: 403);

    using var conn = new SqliteConnection(connectionString);
    conn.Open();
    var wipe = conn.CreateCommand();
    wipe.CommandText = "DELETE FROM scores";
    wipe.ExecuteNonQuery();
    Console.WriteLine("  scoreboard reset");
    return Results.Json(new OkBody(true, "scoreboard reset"));
})
.WithSummary("Reset the scoreboard (instructor only)")
.WithDescription("Requires ?key= matching the RESET_KEY app setting. " +
                 "With no RESET_KEY configured, reset is disabled. Wipes " +
                 "scores only — registered game names are kept and reattach " +
                 "when a bench next appears.")
.Produces<OkBody>()
.Produces<ErrorBody>(StatusCodes.Status403Forbidden);

app.MapGet("/", () => Results.Redirect("/app/")).ExcludeFromDescription();

app.MapOpenApi();
app.MapScalarApiReference(options => options
    .WithTitle("Reaction-Game Scoreboard API")
    .WithDarkMode(true));

// Anything unmatched gets the stdlib server's 404 shape.
app.MapFallback(() => Results.Json(new ErrorBody("no such route"), statusCode: 404))
   .ExcludeFromDescription();

app.Run();

// JSON property names are pinned to the stdlib server's exact spellings —
// do not let a naming policy near these.
sealed record PlayerScore(
    [property: JsonPropertyName("wins")] int Wins,
    [property: JsonPropertyName("false_starts")] int FalseStarts);

sealed record ScoresBody(
    [property: JsonPropertyName("benches")] Dictionary<string, Dictionary<string, PlayerScore>> Benches,
    [property: JsonPropertyName("totals")] Dictionary<string, PlayerScore> Totals,
    [property: JsonPropertyName("names")] Dictionary<string, string> Names);

sealed record ErrorBody([property: JsonPropertyName("error")] string Error);

sealed record OkBody(
    [property: JsonPropertyName("ok")] bool Ok,
    [property: JsonPropertyName("message")] string Message);
