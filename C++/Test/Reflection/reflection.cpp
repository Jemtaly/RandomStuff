#include <iostream>
#include <memory>
#include <utility>

struct IUnknown {
    virtual ~IUnknown() = default;
};

template<typename Impl>
struct Unknown : IUnknown {
    Impl impl;

    template<typename... Args>
    Unknown(Args &&...args)
        : impl(std::forward<Args>(args)...) {}
};

struct IShape : virtual IUnknown {
    virtual int get_shape(void) = 0;
};

template<typename Impl>
struct Shape : IShape {
    Impl impl;

    template<typename... Args>
    Shape(Args &&...args)
        : impl(std::forward<Args>(args)...) {}

    int get_shape(void) {
        return impl.get_shape();
    }
};

struct IColor : virtual IUnknown {
    virtual int get_color(void) = 0;
};

template<typename Impl>
struct Color : IColor {
    Impl impl;

    template<typename... Args>
    Color(Args &&...args)
        : impl(std::forward<Args>(args)...) {}

    int get_color(void) {
        return impl.get_color();
    }
};

struct ISuper : virtual IUnknown {
    virtual int get_super(void) = 0;
};

template<typename Impl>
struct Super : ISuper {
    Impl impl;

    template<typename... Args>
    Super(Args &&...args)
        : impl(std::forward<Args>(args)...) {}

    int get_super(void) {
        return impl.get_super();
    }
};

struct IColorShape
    : virtual IShape
    , virtual IColor {};

template<typename Impl>
struct ColorShape : IColorShape {
    Impl impl;

    template<typename... Args>
    ColorShape(Args &&...args)
        : impl(std::forward<Args>(args)...) {}

    int get_shape(void) {
        return impl.get_shape();
    }

    int get_color(void) {
        return impl.get_color();
    }
};

struct MyColorShapeImpl {
    int shape;
    int color;

    MyColorShapeImpl(int x, int y)
        : shape(x), color(y) {}

    int get_shape(void) {
        return shape;
    }

    int get_color(void) {
        return color;
    }

    ~MyColorShapeImpl() {
        std::cout << "MyColorShapeImpl::~MyColorShapeImpl()" << std::endl;
    }
};

std::shared_ptr<IColorShape> new_my_color_shape(int x, int y) {
    return std::make_shared<ColorShape<MyColorShapeImpl>>(x, y);
}

int main() {
    std::shared_ptr<IUnknown> i_unknown = new_my_color_shape(123, 456);

    if (auto i_shape = std::dynamic_pointer_cast<IShape>(i_unknown)) {
        std::cout << "Cast into IShape successfully, shape = " << i_shape->get_shape() << std::endl;
    } else {
        std::cout << "Cast into IShape failed." << std::endl;
    }

    if (auto i_color = std::dynamic_pointer_cast<IColor>(i_unknown)) {
        std::cout << "Cast into IColor successfully, color = " << i_color->get_color() << std::endl;
    } else {
        std::cout << "Cast into IColor failed." << std::endl;
    }

    if (auto i_super = std::dynamic_pointer_cast<ISuper>(i_unknown)) {
        std::cout << "Cast into ISuper successfully, super = " << i_super->get_super() << std::endl;
    } else {
        std::cout << "Cast into ISuper failed." << std::endl;
    }
}
