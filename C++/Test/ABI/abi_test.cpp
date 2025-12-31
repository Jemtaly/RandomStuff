#include <array>
#include <cstdint>
#include <iostream>
#include <utility>
#include <format>

struct InterfaceMapItem {
    void const *iid;
    void const *pvtbl;
};

struct RTTI {
    std::size_t length;
    InterfaceMapItem imap[];
};

struct CommonHandle {
    RTTI const *prtti;

    void const *dynamicQueryInterface(void const *iid) {
        for (std::size_t i = 0; i < prtti->length; i++) {
            if (iid == prtti->imap[i].iid) {
                return prtti->imap[i].pvtbl;
            }
        }
        return nullptr;
    }
};

template<typename T, std::size_t S>
constexpr std::size_t concatArraysInPlace(std::array<T, S> &r, std::size_t j) {
    return 0;
}

template<typename T, std::size_t S, std::size_t N, std::size_t... Ns>
constexpr std::size_t concatArraysInPlace(std::array<T, S> &r, std::size_t j, std::array<T, N> const &a, std::array<T, Ns> const &...as) {
    for (std::size_t i = 0; i < N; i++, j++) {
        r[j] = a[i];
    }
    return N + concatArraysInPlace(r, j, as...);
}

template<typename T, std::size_t... Ns>
constexpr auto makeRTTI(std::array<T, Ns> const &...as) {
    struct {
        std::size_t length;
        std::array<InterfaceMapItem, (Ns + ...)> imap;
    } r = {0, {}};

    r.length = concatArraysInPlace(r.imap, 0, as...);
    return r;
}

template<typename Self, template<typename> typename... TypeInfos>
struct Handle : CommonHandle {
    static constexpr auto rtti = makeRTTI(TypeInfos<Self>::imap...);

    Handle()
        : CommonHandle{(RTTI *)&rtti} {}

    static constexpr void const *staticQueryInterface(void const *iid) {
        for (std::size_t i = 0; i < rtti.length; i++) {
            if (iid == rtti.imap[i].iid) {
                return rtti.imap[i].pvtbl;
            }
        }
        throw std::logic_error("Static cast failed!");
    }

    template<void const *iid>
    static constexpr void const *staticQueryInterfaceResult = staticQueryInterface(iid);
};

template<typename Self>
struct OwnerPtr {
    Self *pself;

    OwnerPtr<Self>(Self *pself)
        : pself(pself) {}

    operator Self *() && {
        return std::exchange(this->pself, nullptr);
    }

    OwnerPtr<Self>(OwnerPtr<Self> &&other)
        : pself(std::exchange(other.pself, nullptr)) {}

    Self *operator->() {
        return this->pself;
    }

    ~OwnerPtr<Self>() {
        if (this->pself) {
            this->pself->drop();
        }
    }

    OwnerPtr<Self> &operator=(OwnerPtr<Self> other) {
        std::swap(this->pself, other.pself);
        return *this;
    }
};

template<typename Self>
struct RefPtr {
    Self *pself;

    RefPtr<Self>(Self *pself)
        : pself(pself) {}

    operator Self *() {
        return this->pself;
    }

    RefPtr<Self>(OwnerPtr<Self> const &other)
        : pself(other.pself) {}

    RefPtr<Self>(RefPtr<Self> const &other)
        : pself(other.pself) {}

    Self *operator->() {
        return this->pself;
    }

    ~RefPtr<Self>() {}

    RefPtr<Self> &operator=(RefPtr<Self> other) = delete;
};

template<typename FatPtr>
struct Owner : FatPtr {
    Owner<FatPtr>(FatPtr other)
        : FatPtr(other) {}

    operator FatPtr() && {
        return {
            this->pvtbl,
            std::exchange(this->pself, nullptr),
        };
    }

    template<typename Self>
    Owner<FatPtr>(OwnerPtr<Self> &&other) {
        this->pvtbl = static_cast<typename FatPtr::VTable const *>(Self::template staticQueryInterfaceResult<FatPtr::iid>);
        this->pself = std::exchange(other.pself, nullptr);
    }

    Owner<FatPtr>(Owner<FatPtr> &&other) {
        this->pvtbl = &static_cast<typename FatPtr::VTable const &>(*other.pvtbl);
        this->pself = std::exchange(other.pself, nullptr);
    }

    template<typename IFrom, std::conditional_t<std::is_constructible_v<typename FatPtr::VTable const &, typename IFrom::VTable const &>, int, void> = 0>
    Owner<FatPtr>(Owner<IFrom> &&other) {
        this->pvtbl = &static_cast<typename FatPtr::VTable const &>(*other.pvtbl);
        this->pself = std::exchange(other.pself, nullptr);
    }

    template<typename IFrom, std::conditional_t<std::is_constructible_v<typename FatPtr::VTable const &, typename IFrom::VTable const &>, void, int> = 0>
    explicit Owner<FatPtr>(Owner<IFrom> &&other) {
        this->pself = (this->pvtbl = static_cast<typename FatPtr::VTable const *>(other.pself->dynamicQueryInterface(FatPtr::iid)))
                          ? std::exchange(other.pself, nullptr)
                          : nullptr;
    }

    ~Owner<FatPtr>() {
        if (this->pself) {
            this->drop();
        }
    }

    Owner<FatPtr> &operator=(Owner<FatPtr> other) {
        std::swap(this->pvtbl, other.pvtbl);
        std::swap(this->pself, other.pself);
        return *this;
    }
};

template<typename FatPtr>
struct Ref : FatPtr {
    Ref<FatPtr>(FatPtr other)
        : FatPtr(other) {}

    operator FatPtr() {
        return {
            this->pvtbl,
            this->pself,
        };
    }

    template<typename Self>
    Ref<FatPtr>(RefPtr<Self> const &other) {
        this->pvtbl = static_cast<typename FatPtr::VTable const *>(Self::template staticQueryInterfaceResult<FatPtr::iid>);
        this->pself = other.pself;
    }

    template<typename Self>
    Ref<FatPtr>(OwnerPtr<Self> const &other) {
        this->pvtbl = static_cast<typename FatPtr::VTable const *>(Self::template staticQueryInterfaceResult<FatPtr::iid>);
        this->pself = other.pself;
    }

    Ref<FatPtr>(Ref<FatPtr> const &other) {
        this->pvtbl = &static_cast<typename FatPtr::VTable const &>(*other.pvtbl);
        this->pself = other.pself;
    }

    Ref<FatPtr>(Owner<FatPtr> const &other) {
        this->pvtbl = &static_cast<typename FatPtr::VTable const &>(*other.pvtbl);
        this->pself = other.pself;
    }

    template<typename IFrom, std::conditional_t<std::is_constructible_v<typename FatPtr::VTable const &, typename IFrom::VTable const &>, int, void> = 0>
    Ref<FatPtr>(Ref<IFrom> const &other) {
        this->pvtbl = &static_cast<typename FatPtr::VTable const &>(*other.pvtbl);
        this->pself = other.pself;
    }

    template<typename IFrom, std::conditional_t<std::is_constructible_v<typename FatPtr::VTable const &, typename IFrom::VTable const &>, int, void> = 0>
    Ref<FatPtr>(Owner<IFrom> const &other) {
        this->pvtbl = &static_cast<typename FatPtr::VTable const &>(*other.pvtbl);
        this->pself = other.pself;
    }

    template<typename IFrom, std::conditional_t<std::is_constructible_v<typename FatPtr::VTable const &, typename IFrom::VTable const &>, void, int> = 0>
    explicit Ref<FatPtr>(Ref<IFrom> const &other) {
        this->pself = (this->pvtbl = static_cast<typename FatPtr::VTable const *>(other.pself->dynamicQueryInterface(FatPtr::iid)))
                          ? other.pself
                          : nullptr;
    }

    template<typename IFrom, std::conditional_t<std::is_constructible_v<typename FatPtr::VTable const &, typename IFrom::VTable const &>, void, int> = 0>
    explicit Ref<FatPtr>(Owner<IFrom> const &other) {
        this->pself = (this->pvtbl = static_cast<typename FatPtr::VTable const *>(other.pself->dynamicQueryInterface(FatPtr::iid)))
                          ? other.pself
                          : nullptr;
    }

    ~Ref<FatPtr>() {}

    Ref<FatPtr> &operator=(Ref<FatPtr> other) = delete;
};

// IBase
struct FTableIBase {
    void (*drop)(CommonHandle *pself);
};

struct VTableIBase {
    FTableIBase const *pftbl;
};

constexpr void const *IBase_iid = &IBase_iid;

struct IBase {
    using FTable = FTableIBase;
    using VTable = VTableIBase;
    static constexpr void const *iid = IBase_iid;

    VTableIBase const *pvtbl;
    CommonHandle *pself;

    void drop() const {
        return static_cast<VTableIBase const &>(*this->pvtbl).pftbl->drop(this->pself);
    }
};

template<typename Self>
void IBase_drop(CommonHandle *pself) {
    return static_cast<Self *>(pself)->drop();
}

template<typename Self>
FTableIBase const IBase_ftbl = {
    .drop = &IBase_drop<Self>,
};

template<typename Self>
VTableIBase const IBase_vtbl = {
    .pftbl = &IBase_ftbl<Self>,
};

template<typename Self>
struct TypeInfoIBase {
    static constexpr std::array<InterfaceMapItem, 1> imap = {{
        {IBase_iid, &static_cast<VTableIBase const &>(IBase_vtbl<Self>)},
    }};
};

// ICloneable
struct FTableICloneable {
    CommonHandle *(*dup)(CommonHandle *pself);
};

struct VTableICloneable {
    FTableICloneable const *pftbl;
    VTableIBase vtblIBase;

    constexpr operator VTableIBase const &() const & {
        return this->vtblIBase;
    }
};

constexpr void const *ICloneable_iid = &ICloneable_iid;

struct ICloneable {
    using FTable = FTableICloneable;
    using VTable = VTableICloneable;
    static constexpr void const *iid = ICloneable_iid;

    VTableICloneable const *pvtbl;
    CommonHandle *pself;

    void drop() const {
        return static_cast<VTableIBase const &>(*this->pvtbl).pftbl->drop(this->pself);
    }

    Owner<ICloneable> dup() const {
        return {{
            this->pvtbl,
            static_cast<VTableICloneable const &>(*this->pvtbl).pftbl->dup(this->pself),
        }};
    }
};

template<typename Self>
CommonHandle *ICloneable_dup(CommonHandle *pself) {
    return static_cast<Self *>(static_cast<Self *>(pself)->dup());
}

template<typename Self>
FTableICloneable const ICloneable_ftbl = {
    .dup = &ICloneable_dup<Self>,
};

template<typename Self>
VTableICloneable const ICloneable_vtbl = {
    .pftbl = &ICloneable_ftbl<Self>,
    .vtblIBase = {
        .pftbl = &IBase_ftbl<Self>,
    },
};

template<typename Self>
struct TypeInfoICloneable {
    static constexpr std::array<InterfaceMapItem, 2> imap = {{
        {IBase_iid, &static_cast<VTableIBase const &>(ICloneable_vtbl<Self>)},
        {ICloneable_iid, &static_cast<VTableICloneable const &>(ICloneable_vtbl<Self>)},
    }};
};

// IColorable
struct FTableIColorable {
    uint32_t (*getColor)(CommonHandle *pself);
    void (*setColor)(CommonHandle *pself, uint32_t color);
};

struct VTableIColorable {
    FTableIColorable const *pftbl;
    VTableICloneable vtblICloneable;

    constexpr operator VTableIBase const &() const & {
        return this->vtblICloneable.vtblIBase;
    }

    constexpr operator VTableICloneable const &() const & {
        return this->vtblICloneable;
    }
};

constexpr void const *IColorable_iid = &IColorable_iid;

struct IColorable {
    using FTable = FTableIColorable;
    using VTable = VTableIColorable;
    static constexpr void const *iid = IColorable_iid;

    VTableIColorable const *pvtbl;
    CommonHandle *pself;

    void drop() const {
        return static_cast<VTableIBase const &>(*this->pvtbl).pftbl->drop(this->pself);
    }

    Owner<IColorable> dup() const {
        return {{
            this->pvtbl,
            static_cast<VTableICloneable const &>(*this->pvtbl).pftbl->dup(this->pself),
        }};
    }

    uint32_t getColor() const {
        return static_cast<VTableIColorable const &>(*this->pvtbl).pftbl->getColor(this->pself);
    }

    void setColor(uint32_t color) const {
        return static_cast<VTableIColorable const &>(*this->pvtbl).pftbl->setColor(this->pself, color);
    }
};

template<typename Self>
uint32_t IColorable_getColor(CommonHandle *pself) {
    return static_cast<Self *>(pself)->getColor();
}

template<typename Self>
void IColorable_setColor(CommonHandle *pself, uint32_t color) {
    return static_cast<Self *>(pself)->setColor(color);
}

template<typename Self>
FTableIColorable const IColorable_ftbl = {
    .getColor = &IColorable_getColor<Self>,
    .setColor = &IColorable_setColor<Self>,
};

template<typename Self>
VTableIColorable const IColorable_vtbl = {
    .pftbl = &IColorable_ftbl<Self>,
    .vtblICloneable = {
        .pftbl = &ICloneable_ftbl<Self>,
        .vtblIBase = {
            .pftbl = &IBase_ftbl<Self>,
        },
    },
};

template<typename Self>
struct TypeInfoIColorable {
    static constexpr std::array<InterfaceMapItem, 3> imap = {{
        {IBase_iid, &static_cast<VTableIBase const &>(IColorable_vtbl<Self>)},
        {ICloneable_iid, &static_cast<VTableICloneable const &>(IColorable_vtbl<Self>)},
        {IColorable_iid, &static_cast<VTableIColorable const &>(IColorable_vtbl<Self>)},
    }};
};

// IShape
struct FTableIShape {
    float (*calculateArea)(CommonHandle *pself);
};

struct VTableIShape {
    FTableIShape const *pftbl;
    VTableICloneable vtblICloneable;

    constexpr operator VTableIBase const &() const & {
        return this->vtblICloneable.vtblIBase;
    }

    constexpr operator VTableICloneable const &() const & {
        return this->vtblICloneable;
    }
};

constexpr void const *IShape_iid = &IShape_iid;

struct IShape {
    using FTable = FTableIShape;
    using VTable = VTableIShape;
    static constexpr void const *iid = IShape_iid;

    VTableIShape const *pvtbl;
    CommonHandle *pself;

    void drop() const {
        return static_cast<VTableIBase const &>(*this->pvtbl).pftbl->drop(this->pself);
    }

    Owner<IShape> dup() const {
        return {{
            this->pvtbl,
            static_cast<VTableICloneable const &>(*this->pvtbl).pftbl->dup(this->pself),
        }};
    }

    float calculateArea() const {
        return static_cast<VTableIShape const &>(*this->pvtbl).pftbl->calculateArea(this->pself);
    }
};

template<typename Self>
float IShape_calculateArea(CommonHandle *pself) {
    return static_cast<Self *>(pself)->calculateArea();
}

template<typename Self>
FTableIShape const IShape_ftbl = {
    .calculateArea = &IShape_calculateArea<Self>,
};

template<typename Self>
VTableIShape const IShape_vtbl = {
    .pftbl = &IShape_ftbl<Self>,
    .vtblICloneable = {
        .pftbl = &ICloneable_ftbl<Self>,
        .vtblIBase = {
            .pftbl = &IBase_ftbl<Self>,
        },
    },
};

template<typename Self>
struct TypeInfoIShape {
    static constexpr std::array<InterfaceMapItem, 3> imap = {{
        {IBase_iid, &static_cast<VTableIBase const &>(IShape_vtbl<Self>)},
        {ICloneable_iid, &static_cast<VTableICloneable const &>(IShape_vtbl<Self>)},
        {IShape_iid, &static_cast<VTableIShape const &>(IShape_vtbl<Self>)},
    }};
};

// IShowable
struct FTableIShowable {
    void (*show)(CommonHandle *pself);
};

struct VTableIShowable {
    FTableIShowable const *pftbl;
    VTableIColorable vtblIColorable;
    VTableIShape vtblIShape;

    constexpr operator VTableIBase const &() const & {
        return this->vtblIColorable.vtblICloneable.vtblIBase;
    }

    constexpr operator VTableICloneable const &() const & {
        return this->vtblIColorable.vtblICloneable;
    }

    constexpr operator VTableIColorable const &() const & {
        return this->vtblIColorable;
    }

    constexpr operator VTableIShape const &() const & {
        return this->vtblIShape;
    }
};

constexpr void const *IShowable_iid = &IShowable_iid;

struct IShowable {
    using FTable = FTableIShowable;
    using VTable = VTableIShowable;
    static constexpr void const *iid = IShowable_iid;

    VTableIShowable const *pvtbl;
    CommonHandle *pself;

    void drop() const {
        return static_cast<VTableIBase const &>(*this->pvtbl).pftbl->drop(this->pself);
    }

    Owner<IShowable> dup() const {
        return {{
            this->pvtbl,
            static_cast<VTableICloneable const &>(*this->pvtbl).pftbl->dup(this->pself),
        }};
    }

    uint32_t getColor() const {
        return static_cast<VTableIColorable const &>(*this->pvtbl).pftbl->getColor(this->pself);
    }

    void setColor(uint32_t color) const {
        return static_cast<VTableIColorable const &>(*this->pvtbl).pftbl->setColor(this->pself, color);
    }

    float calculateArea() const {
        return static_cast<VTableIShape const &>(*this->pvtbl).pftbl->calculateArea(this->pself);
    }

    void show() const {
        return static_cast<VTableIShowable const &>(*this->pvtbl).pftbl->show(this->pself);
    }
};

template<typename Self>
void IShowable_show(CommonHandle *pself) {
    return static_cast<Self *>(pself)->show();
}

template<typename Self>
FTableIShowable const IShowable_ftbl = {
    .show = &IShowable_show<Self>,
};

template<typename Self>
VTableIShowable const IShowable_vtbl = {
    .pftbl = &IShowable_ftbl<Self>,
    .vtblIColorable = {
        .pftbl = &IColorable_ftbl<Self>,
        .vtblICloneable = {
            .pftbl = &ICloneable_ftbl<Self>,
            .vtblIBase = {
                .pftbl = &IBase_ftbl<Self>,
            },
        },
    },
    .vtblIShape = {
        .pftbl = &IShape_ftbl<Self>,
        .vtblICloneable = {
            .pftbl = &ICloneable_ftbl<Self>,
            .vtblIBase = {
                .pftbl = &IBase_ftbl<Self>,
            },
        },
    },
};

template<typename Self>
struct TypeInfoIShowable {
    static constexpr std::array<InterfaceMapItem, 5> imap = {{
        {IBase_iid, &static_cast<VTableIBase const &>(IShowable_vtbl<Self>)},
        {ICloneable_iid, &static_cast<VTableICloneable const &>(IShowable_vtbl<Self>)},
        {IColorable_iid, &static_cast<VTableIColorable const &>(IShowable_vtbl<Self>)},
        {IShape_iid, &static_cast<VTableIShape const &>(IShowable_vtbl<Self>)},
        {IShowable_iid, &static_cast<VTableIShowable const &>(IShowable_vtbl<Self>)},
    }};
};

// Source
template<typename Self>
struct SharedMemory {
    std::size_t count = 0;

    template<typename... Args>
    static OwnerPtr<Self> create(Args &&...args) {
        Self *res = new Self(std::forward<Args>(args)...);
        res->count = 1;
        return res;
    }

    OwnerPtr<Self> dup() {
        ++count;
        return static_cast<Self *>(this);
    }

    void drop() {
        if (--count != 0) {
            return;
        }
        delete static_cast<Self *>(this);
    }
};

template<typename ImplShowable>
struct asIShowable
    : ImplShowable
    , SharedMemory<asIShowable<ImplShowable>>
    , Handle<asIShowable<ImplShowable>, TypeInfoIShowable> {
    template<typename... Args>
    asIShowable<ImplShowable>(Args &&...args)
        : ImplShowable(std::forward<Args>(args)...) {}
};

template<typename ImplColorable>
struct asIColorable
    : ImplColorable
    , SharedMemory<asIColorable<ImplColorable>>
    , Handle<asIColorable<ImplColorable>, TypeInfoIColorable> {
    template<typename... Args>
    asIColorable<ImplColorable>(Args &&...args)
        : ImplColorable(std::forward<Args>(args)...) {}
};

template<typename ImplShape>
struct asIShape
    : ImplShape
    , SharedMemory<asIShape<ImplShape>>
    , Handle<asIShape<ImplShape>, TypeInfoIShape> {
    template<typename... Args>
    asIShape<ImplShape>(Args &&...args)
        : ImplShape(std::forward<Args>(args)...) {}
};

template<typename ImplCloneable>
struct asICloneable
    : ImplCloneable
    , SharedMemory<asICloneable<ImplCloneable>>
    , Handle<asICloneable<ImplCloneable>, TypeInfoICloneable> {
    template<typename... Args>
    asICloneable<ImplCloneable>(Args &&...args)
        : ImplCloneable(std::forward<Args>(args)...) {}
};

template<typename ImplBase>
struct asIBase
    : ImplBase
    , SharedMemory<asIBase<ImplBase>>
    , Handle<asIBase<ImplBase>, TypeInfoIBase> {
    template<typename... Args>
    asIBase<ImplBase>(Args &&...args)
        : ImplBase(std::forward<Args>(args)...) {}
};

struct MyColorable {
    uint32_t color;

    MyColorable(uint32_t color)
        : color(color) {}

    uint32_t getColor() {
        return color;
    }

    void setColor(uint32_t color) {
        this->color = color;
    }
};

struct MyShowable {
    float x;
    float y;
    uint32_t color;

    MyShowable(float x, float y, uint32_t color)
        : x(x), y(y), color(color) {}

    ~MyShowable() {}

    uint32_t getColor() {
        return color;
    }

    void setColor(uint32_t color) {
        this->color = color;
    }

    float calculateArea() {
        return x * y;
    }

    void show() {
        std::cout << std::format("{} * {}: 0x{:08x}\n", x, y, color);
    }
};

void copyColor(Ref<IColorable> from, Ref<IColorable> to) {
    to.setColor(from.getColor());
}

using MyShowableExported = asIShowable<MyShowable>;
using MyColorableExported = asIColorable<MyColorable>;

int main() {
    Owner<IShowable> showable_obj = MyShowableExported::create(10.0, 10.0, 0x00000000);
    Owner<IColorable> colorable_obj = MyColorableExported::create(0xffffff00);
    showable_obj.show();
    copyColor(colorable_obj, showable_obj);
    showable_obj.show();
}
