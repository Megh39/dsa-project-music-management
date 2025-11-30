# %%
import csv
from flask import Flask, render_template, request


# ----------------------------------------------------
# SONG CLASS
# ----------------------------------------------------
class Song:
    def __init__(self, song_id, title, artist, album, genre, duration, year):
        self.song_id = song_id
        self.title = title
        self.artist = artist
        self.album = album
        self.genre = genre
        self.duration = int(duration)
        self.year = int(year)

    def __repr__(self):
        return f"[{self.song_id}] {self.title} by {self.artist} ({self.album}, {self.year}) - {self.genre}, {self.duration}s"


# %%


# ----------------------------------------------------
# HASH TABLE FOR SONG LIBRARY
# ----------------------------------------------------
class HashNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class HashTable:
    def __init__(self, size=100):
        self.size = size
        self.table = [None] * size

    def _hash(self, key):
        h = 5381
        for c in key:
            h = h * 33 + ord(c)
        return h % self.size

    def insert(self, key, value):
        index = self._hash(key)
        node = self.table[index]

        if not node:
            self.table[index] = HashNode(key, value)
            return

        while node.next:
            if node.key == key:
                node.value = value
                return
            node = node.next

        node.next = HashNode(key, value)

    def search(self, key):
        index = self._hash(key)
        node = self.table[index]

        while node:
            if node.key == key:
                return node.value
            node = node.next
        return None

    def search_by_title(self, title):
        title = title.strip().lower()
        matches = []

        for bucket in self.table:
            node = bucket
            while node:
                if node.value.title.strip().lower() == title:
                    matches.append(node.value)
                node = node.next

        return matches

    def search_by_partial_title(self, partial):
        partial = partial.strip().lower()
        matches = []

        for bucket in self.table:
            node = bucket
            while node:
                if partial in node.value.title.lower():
                    matches.append(node.value)
                node = node.next

        return matches

    def delete(self, key):
        index = self._hash(key)
        node = self.table[index]
        prev = None

        while node:
            if node.key == key:
                if prev:
                    prev.next = node.next
                else:
                    self.table[index] = node.next
                return True
            prev, node = node, node.next

        return False

    def display_all_songs(self):
        out = []
        for bucket in self.table:
            node = bucket
            while node:
                out.append(str(node.value))
                node = node.next
        return "\n".join(out) if out else "Library is empty."

    def display(self):
        out = []
        for i in range(self.size):
            node = self.table[i]
            if node:
                chain = []
                temp = node
                while temp:
                    chain.append(temp.key)
                    temp = temp.next
                out.append(f"Bucket {i}: " + " -> ".join(chain))
        return "\n".join(out) if out else "Hash table is empty."


# %%


# ----------------------------------------------------
# LINKED LIST FOR PLAYLIST
# ----------------------------------------------------
class Node:
    def __init__(self, song):
        self.song = song
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def insert_at_start(self, song):
        new_node = Node(song)
        new_node.next = self.head
        self.head = new_node

    def insert_at_end(self, song):
        new_node = Node(song)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node

    def delete_song(self, song_id):
        current = self.head
        prev = None

        while current and current.song.song_id != song_id:
            prev = current
            current = current.next

        if not current:
            print("Song not found.")
            return False

        if not prev:
            self.head = current.next
        else:
            prev.next = current.next

        print("Deleted:", current.song.title)
        return True

    def search(self, song_id):
        current = self.head
        while current:
            if current.song.song_id == song_id:
                return current.song
            current = current.next
        return None

    def search_by_title(self, title):
        title = title.lower()
        current = self.head
        results = []

        while current:
            if current.song.title.lower() == title:
                results.append(current.song)
            current = current.next

        return results

    def search_by_partial_title(self, partial):
        partial = partial.lower()
        current = self.head
        results = []

        while current:
            if partial in current.song.title.lower():
                results.append(current.song)
            current = current.next

        return results

    def display(self):
        if not self.head:
            print("Playlist is empty.")
            return
        out = []
        current = self.head
        while current:
            out.append(str(current.song))
            current = current.next
        return "\n".join(out)

    def insert_after(self, target_id, song):
        current = self.head
        while current and current.song.song_id != target_id:
            current = current.next

        if not current:
            print("Target song not found.")
            return False

        new_node = Node(song)
        new_node.next = current.next
        current.next = new_node
        print(f"Inserted {song.title} after {current.song.title}")
        return True

    def move_up(self, song_id):
        if not self.head or not self.head.next:
            return False

        prev = None
        curr = self.head

        while curr and curr.song.song_id != song_id:
            prev_prev = prev
            prev = curr
            curr = curr.next

        if not curr or not prev:
            return False

        prev.next = curr.next
        curr.next = prev

        if prev_prev:
            prev_prev.next = curr
        else:
            self.head = curr

        return True

    def move_down(self, song_id):
        curr = self.head
        prev = None

        while curr and curr.song.song_id != song_id:
            prev = curr
            curr = curr.next

        if not curr or not curr.next:
            return False

        nxt = curr.next
        curr.next = nxt.next
        nxt.next = curr

        if prev:
            prev.next = nxt
        else:
            self.head = nxt

        return True

    def reverse(self):
        prev = None
        current = self.head

        while current:
            nxt = current.next
            current.next = prev
            prev = current
            current = nxt

        self.head = prev


# %%


# ----------------------------------------------------
# QUEUE FOR PLAYBACK
# ----------------------------------------------------
class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, song):
        self.items.append(song)
        return f"Added to queue: {song.title}"

    def dequeue(self):
        if not self.items:
            return "Queue empty.", None
        song = self.items.pop(0)
        return f"Now playing: {song.title}", song

    def peek(self):
        if not self.items:
            return None
        return self.items[0]

    def display(self):
        if not self.items:
            return "Queue is empty."

        out = ["Current Queue:"]
        for i, song in enumerate(self.items, start=1):
            out.append(f"{i}. {song.title} by {song.artist}")

        return "\n".join(out)

    def find_song_for_queue(text):
        # ID
        s = library.search(text)
        if s:
            return s

        # full title
        exact = library.search_by_title(text)
        if exact:
            return exact[0]

        # partial
        partial = library.search_by_partial_title(text)
        if partial:
            return partial[0]

        return None

    def replay(self, stack):
        song = stack.pop()
        if not song:
            return "No song to replay."

        self.enqueue(song)
        return f"Replaying: {song.title}"


# %%


# ----------------------------------------------------
# STACK FOR RECENTLY PLAYED
# ----------------------------------------------------
class Stack:
    def __init__(self):
        self.items = []

    def push(self, song):
        self.items.append(song)

    def pop(self):
        if not self.items:
            print("No recently played songs.")
            return None
        return self.items.pop()

    def display_list(self):
        if not self.items:
            return "No recently played songs."
        return "\n".join(str(s) for s in reversed(self.items))

    def display(self):
        if not self.items:
            print("No recently played songs.")
            return
        print("Recently Played:")
        for song in reversed(self.items):
            print(song)


# %%


# ----------------------------------------------------
# LOAD SONGS FROM CSV
# ----------------------------------------------------
def load_songs(filename):
    songs = []
    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = Song(
                row["song_id"],
                row["title"],
                row["artist"],
                row["album"],
                row["genre"],
                int(row["duration_sec"]),
                int(row["release_year"]),
            )
            songs.append(song)
    return songs


songs = load_songs("songs_dataset_updated.csv")


library = HashTable(size=60)
playlist = LinkedList()
queue = Queue()
history = Stack()

# Insert all into hash table
for s in songs:
    library.insert(s.song_id, s)

# ----------------------------------------------------
# FLASK APP
# ----------------------------------------------------
# ----------------------------------------------------
# FLASK APP
# ----------------------------------------------------
app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# ---------------------- LIBRARY ----------------------
@app.route("/library", methods=["POST"])
def library_action():
    song_id = request.form.get("song_id", "").strip()
    action = request.form.get("action")

    # SEARCH
    if action == "search":
        q = song_id.lower()

        # 1 ID match
        by_id = library.search(song_id.upper())
        if by_id:
            return render_template(
                "index.html",
                active_section="library-section",
                library_last_query=song_id,
                library_output_search=str(by_id),
            )

        # 2 exact title
        by_title = library.search_by_title(q)
        if by_title:
            return render_template(
                "index.html",
                active_section="library-section",
                library_last_query=song_id,
                library_output_search="\n".join(str(s) for s in by_title),
            )

        # 3 partial title
        by_partial = library.search_by_partial_title(q)
        if by_partial:
            return render_template(
                "index.html",
                active_section="library-section",
                library_last_query=song_id,
                library_output_search="\n".join(str(s) for s in by_partial),
            )

        return render_template(
            "index.html",
            active_section="library-section",
            library_last_query=song_id,
            library_output_search="No match found.",
        )

    # DELETE
    if action == "delete":
        ok = library.delete(song_id)
        return render_template(
            "index.html",
            active_section="library-section",
            library_last_query=song_id,
            library_output_search="Deleted." if ok else "Not found.",
        )


@app.route("/library/display", methods=["POST"])
def library_display():
    return render_template(
        "index.html",
        active_section="library-section",
        library_output_buckets=library.display(),
    )


@app.route("/library/all", methods=["POST"])
def library_all():
    return render_template(
        "index.html",
        active_section="library-section",
        library_output_all=library.display_all_songs(),
    )


# ---------------------- PLAYLIST ----------------------
@app.route("/playlist", methods=["POST"])
def playlist_action():
    action = request.form.get("action")
    song_id = request.form.get("song_id")

    # reverse does NOT need song_id
    if action == "reverse":
        playlist.reverse()
        return render_template(
            "index.html",
            active_section="playlist-section",
            playlist_output="Playlist reversed.",
            playlist_reorder_song=None,
        )

    # INSERT AFTER
    if action == "insert_after":
        target_id = request.form.get("target_id")

        if not song_id or not target_id:
            return render_template(
                "index.html",
                active_section="playlist-section",
                playlist_output="Both song_id and target_id required.",
                playlist_insert_new=song_id,
                playlist_insert_target=target_id,
            )

        song = library.search(song_id)
        target_song = library.search(target_id)

        if not song or not target_song:
            return render_template(
                "index.html",
                active_section="playlist-section",
                playlist_output="Song or target not found in library.",
                playlist_insert_new=song_id,
                playlist_insert_target=target_id,
            )

        playlist.insert_after(target_id, song)

        return render_template(
            "index.html",
            active_section="playlist-section",
            playlist_output=f"Inserted {song.title} after {target_song.title}",
            playlist_insert_new=song_id,
            playlist_insert_target=target_id,
        )

    # MOVE UP / MOVE DOWN
    if action in ["move_up", "move_down"]:
        if not song_id:
            return render_template(
                "index.html",
                active_section="playlist-section",
                playlist_output="Song ID required.",
                playlist_reorder_song=song_id,
            )

        ok = (
            playlist.move_up(song_id)
            if action == "move_up"
            else playlist.move_down(song_id)
        )

        return render_template(
            "index.html",
            active_section="playlist-section",
            playlist_output="Success." if ok else "Cannot move.",
            playlist_reorder_song=song_id,
        )

    # ADD_START / ADD_END / DELETE
    if action in ["add_start", "add_end", "delete"]:
        if not song_id:
            return render_template(
                "index.html",
                active_section="playlist-section",
                playlist_output="Song ID required.",
                playlist_modify_song=song_id,
            )

        song = library.search(song_id)

        if not song and action != "delete":
            return render_template(
                "index.html",
                active_section="playlist-section",
                playlist_output="Song not found in library.",
                playlist_modify_song=song_id,
            )

        if action == "add_start":
            playlist.insert_at_start(song)
            msg = "Inserted at start."

        elif action == "add_end":
            playlist.insert_at_end(song)
            msg = "Inserted at end."

        else:  # delete
            removed = playlist.delete_song(song_id)
            msg = "Deleted." if removed else "Song not found."

        return render_template(
            "index.html",
            active_section="playlist-section",
            playlist_output=msg,
            playlist_modify_song=song_id,
        )


@app.route("/playlist/display", methods=["POST"])
def playlist_display():
    return render_template(
        "index.html",
        active_section="playlist-section",
        playlist_output=playlist.display(),
    )


# ---------------------- QUEUE ----------------------
def find_song(text):
    if library.search(text):
        return library.search(text)

    t = library.search_by_title(text.lower())
    if t:
        return t[0]

    p = library.search_by_partial_title(text.lower())
    if p:
        return p[0]

    return None

@app.route("/queue", methods=["POST"])
def queue_action():
    action = request.form.get("action")
    song_id = request.form.get("song_id", "").strip()

    args = {
        "active_section": "queue-section",
        "queue_last_song": song_id,
        "queue_output_display": "",       # LEFT CARD
        "queue_output": queue.display(),  # RIGHT CARD
    }

    # ENQUEUE
    if action == "enqueue":
        song = find_song(song_id)
        if not song:
            args["queue_output_display"] = "Song not found."
            return render_template("index.html", **args)

        args["queue_output_display"] = queue.enqueue(song)
        args["queue_output"] = queue.display()
        return render_template("index.html", **args)

    # DEQUEUE
    if action == "dequeue":
        msg, song = queue.dequeue()
        if song:
            history.push(song)

        args["queue_output_display"] = msg
        args["queue_output"] = queue.display()
        args["queue_last_song"] = ""
        return render_template("index.html", **args)

    # PEEK
    if action == "peek":
        song = queue.peek()
        args["queue_output_display"] = str(song) if song else "Queue empty."
        args["queue_output"] = queue.display()
        return render_template("index.html", **args)

    # REPLAY
    if action == "replay":
        args["queue_output_display"] = queue.replay(history)
        args["queue_output"] = queue.display()
        args["queue_last_song"] = ""
        return render_template("index.html", **args)

    args["queue_output_display"] = "Invalid action."
    return render_template("index.html", **args)

@app.route("/queue/display", methods=["POST"])
def queue_display():
    return render_template(
        "index.html",
        active_section="queue-section",
        queue_output=queue.display(),      # right box
        queue_output_display="",           # left box stays untouched
        queue_last_song=""
    )

# ---------------------- HISTORY ----------------------
@app.route("/history", methods=["POST"])
def history_action():
    action = request.form.get("action")

    if action == "undo":
        song = history.pop()
        if not song:
            return render_template(
                "index.html",
                active_section="history-section",
                history_output="History empty.",
            )

        queue.enqueue(song)
        return render_template(
            "index.html",
            active_section="history-section",
            history_output=f"Restored to queue: {song.title}",
        )

    if action == "clear":
        history.items.clear()
        return render_template(
            "index.html",
            active_section="history-section",
            history_output="History cleared.",
        )


@app.route("/history/display", methods=["POST"])
def history_display():
    return render_template(
        "index.html",
        active_section="history-section",
        history_output=history.display_list(),
    )


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
