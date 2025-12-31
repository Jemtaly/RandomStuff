#include <Windows.h>
#include <mmsystem.h>

#include <array>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>

#pragma comment(lib, "winmm.lib")

template<uint16_t BytesPerSample, typename Value, typename = std::enable_if_t<std::is_floating_point<Value>::value>>
std::array<char, BytesPerSample> getSampleInt(Value raw) {
    Value amplitude = exp2(BytesPerSample * 8 - 1);
    Value bias = BytesPerSample == 1 ? amplitude / 2 : 0.0;
    Value max = nextafter(bias + amplitude, bias);
    Value min = nextafter(bias - amplitude, bias);

    Value scaled = bias + raw * amplitude;
    if (scaled > max) {
        scaled = max;
    } else if (scaled < min) {
        scaled = min;
    }

    std::array<char, BytesPerSample> sampleBytes;
    for (uint16_t i = 0; i < BytesPerSample; i++) {
        sampleBytes[i] = static_cast<char>(scaled / exp2(i * 8));
    }
    return sampleBytes;
}

template<uint16_t BytesPerSample, typename Value, typename = std::enable_if_t<std::is_integral<Value>::value>>
std::array<char, BytesPerSample> getSampleFloat(Value raw) {
    std::array<char, BytesPerSample> sampleBytes;
    if constexpr (BytesPerSample == 4) {
        float f = static_cast<float>(raw);
        std::memcpy(sampleBytes.data(), &f, BytesPerSample);
    } else if constexpr (BytesPerSample == 8) {
        double d = static_cast<double>(raw);
        std::memcpy(sampleBytes.data(), &d, BytesPerSample);
    } else {
        static_assert(BytesPerSample == 4 || BytesPerSample == 8, "Unsupported BytesPerSample for Float format");
    }
    return sampleBytes;
}

template<uint16_t AudioFormat, uint16_t BytesPerSample, typename Value>
std::array<char, BytesPerSample> getSample(Value raw) {
    if constexpr (AudioFormat == 1) {  // PCM
        return getSampleInt<BytesPerSample, Value>(raw);
    } else if constexpr (AudioFormat == 3) {  // IEEE Float
        return getSampleFloat<BytesPerSample, Value>(raw);
    } else {
        static_assert(AudioFormat == 1 || AudioFormat == 3, "Unsupported Audio Format");
    }
}

struct WavHeader {
    char fileTypeBlockId[4];
    uint32_t fileSize;
    char fileFormatId[4];
    char formatBlockId[4];
    uint32_t blockSize;

    struct Format {
        uint16_t audioFormat;
        uint16_t samplesPerBlock;
        uint32_t blocksPerSec;
        uint32_t bytesPerSec;
        uint16_t bytesPerBlock;
        uint16_t bitsPerSample;
    } fmt;

    char dataBlockId[4];
    uint32_t dataSize;
};

template<uint16_t AudioFormat, uint16_t BytesPerSample, uint16_t SamplesPerBlock>
class WavWriter {
    uint32_t const blocksPerSec;
    std::vector<std::array<std::array<char, BytesPerSample>, SamplesPerBlock>> samples;

public:
    WavWriter(uint32_t rate)
        : blocksPerSec(rate) {}

    template<typename... Values, typename = std::enable_if_t<sizeof...(Values) == SamplesPerBlock>>
    void writeSample(Values... vals) {
        samples.push_back({getSample<AudioFormat, BytesPerSample>(vals)...});
    }

    uint32_t getSampleRate() const {
        return blocksPerSec;
    }

    WavHeader getWavHeader() const {
        WavHeader header;
        std::memcpy(header.fileTypeBlockId, "RIFF", 4);
        header.fileSize = sizeof(WavHeader) - 8 + samples.size() * SamplesPerBlock * BytesPerSample;
        std::memcpy(header.fileFormatId, "WAVE", 4);
        std::memcpy(header.formatBlockId, "fmt ", 4);
        header.blockSize = 16;
        header.fmt.audioFormat = AudioFormat;
        header.fmt.samplesPerBlock = SamplesPerBlock;
        header.fmt.blocksPerSec = blocksPerSec;
        header.fmt.bytesPerSec = blocksPerSec * SamplesPerBlock * BytesPerSample;
        header.fmt.bytesPerBlock = SamplesPerBlock * BytesPerSample;
        header.fmt.bitsPerSample = BytesPerSample * 8;
        std::memcpy(header.dataBlockId, "data", 4);
        header.dataSize = samples.size() * SamplesPerBlock * BytesPerSample;
        return header;
    }

    size_t getTotalBufferSize() const {
        return sizeof(WavHeader) + samples.size() * SamplesPerBlock * BytesPerSample;
    }

    void writeToBuffer(char *buffer) {
        WavHeader header = getWavHeader();
        std::memcpy(buffer, &header, sizeof(WavHeader));
        char *ptr = buffer + sizeof(WavHeader);
        for (auto const &sample : samples) {
            for (auto const &channelData : sample) {
                std::memcpy(ptr, channelData.data(), BytesPerSample);
                ptr += BytesPerSample;
            }
        }
    }

    void writeToStream(std::ofstream &ofs) {
        WavHeader header = getWavHeader();
        ofs.write(reinterpret_cast<char const *>(&header), sizeof(WavHeader));
        for (auto const &sample : samples) {
            for (auto const &channelData : sample) {
                ofs.write(channelData.data(), BytesPerSample);
            }
        }
    }
};

template<uint16_t AudioFormat, uint16_t BytesPerSample, uint16_t SamplesPerBlock>
void writeTone(WavWriter<AudioFormat, BytesPerSample, SamplesPerBlock> &wavWriter, double freq, double duration) {
    uint32_t d = static_cast<uint32_t>(wavWriter.getSampleRate() * duration);
    uint32_t f = static_cast<uint32_t>(wavWriter.getSampleRate() / freq + 0.5);
    std::vector<double> seed(f + d);
    for (uint32_t i = 0; i < f; i++) {
        seed[i] = static_cast<double>(rand()) / static_cast<double>(RAND_MAX);  // [0.0, 1.0)
    }
    for (uint32_t i = 0; i < d; i++) {
        wavWriter.writeSample(seed[i]);
        seed[i + f] = (seed[i] + seed[i + 1]) * 0.5;
    }
}

template<uint16_t AudioFormat, uint16_t BytesPerSample, uint16_t SamplesPerBlock>
void playSound(WavWriter<AudioFormat, BytesPerSample, SamplesPerBlock> &wavWriter) {
    size_t bufSize = wavWriter.getTotalBufferSize();
    char *buffer = new char[bufSize];
    wavWriter.writeToBuffer(buffer);
    PlaySound((LPCSTR)buffer, NULL, SND_MEMORY | SND_SYNC);
    delete[] buffer;
}

template<uint16_t AudioFormat, uint16_t BytesPerSample, uint16_t SamplesPerBlock>
void saveSound(WavWriter<AudioFormat, BytesPerSample, SamplesPerBlock> &wavWriter, std::string const &filename) {
    std::ofstream ofs(filename, std::ios::binary);
    wavWriter.writeToStream(ofs);
    ofs.close();
}

int main(int argc, char *argv[]) {
    WavWriter<1, 2, 1> wavWriter(44100);
    for (auto i : {0, 2, 4, 5, 7, 9, 11, 12}) {
        writeTone(wavWriter, 440.0 * exp2(1.0 / 12 * i), 1.0);
    }
    saveSound(wavWriter, "output.wav");
    return 0;
}
