import { reactive } from "vue";

export const playerStore = reactive({
  currentTrack: null,
  playlist: [],
  currentIndex: -1,
  isPlaying: false,

  play(track, currentPlaylist = []) {
    this.currentTrack = track;
    this.isPlaying = true;
    if (currentPlaylist.length > 0) {
      this.playlist = currentPlaylist;
      this.currentIndex = this.playlist.findIndex((t) => t.id === track.id);
    }
  },

  playNext() {
    if (
      this.playlist.length > 0 &&
      this.currentIndex < this.playlist.length - 1
    ) {
      this.currentIndex++;
      this.currentTrack = this.playlist[this.currentIndex];
      this.isPlaying = true;
    }
  },

  playPrev() {
    if (this.playlist.length > 0 && this.currentIndex > 0) {
      this.currentIndex--;
      this.currentTrack = this.playlist[this.currentIndex];
      this.isPlaying = true;
    }
  },
});
