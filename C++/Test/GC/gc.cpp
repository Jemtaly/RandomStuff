#include <unordered_set>
#include <utility>

class GCManager;

class GCObject {
public:
    virtual ~GCObject() = default;

    void traverseAndMark() {
        if (marked) {
            return;
        }
        marked = true;
        traverseAndMarkImpl();
    }

protected:
    virtual void traverseAndMarkImpl() {}

private:
    GCObject *next = nullptr;
    bool marked = false;

    friend GCManager;
};

class GCManager {
public:
    template<typename T, typename... Args>
    T *alloc(Args &&...args) {
        T *obj = new T(std::forward<Args>(args)...);
        registerObject(obj);
        return obj;
    }

    ~GCManager() {
        while (head) {
            GCObject *record = head;
            head = head->next;
            delete record;
        }
    }

    void addRoot(GCObject *obj) {
        roots.insert(obj);
    }

    void removeRoot(GCObject *obj) {
        roots.erase(obj);
    }

    void collect() {
        mark();
        sweep();
    }

private:
    void registerObject(GCObject *obj) {
        obj->next = head;
        head = obj;
    }

    void mark() {
        for (GCObject *root : roots) {
            root->traverseAndMark();
        }
    }

    void sweep() {
        GCObject **it_ptr = &head;
        while (*it_ptr) {
            if ((*it_ptr)->marked) {
                (*it_ptr)->marked = false;
                it_ptr = &(*it_ptr)->next;
            } else {
                GCObject *record = *it_ptr;
                *it_ptr = (*it_ptr)->next;
                delete record;
            }
        }
    }

    GCObject *head = nullptr;
    std::unordered_set<GCObject *> roots;
};

#include <chrono>
#include <iostream>

template<typename Func, typename... Args>
std::chrono::nanoseconds test(Func const &func, Args &&...args) {
    auto start = std::chrono::high_resolution_clock::now();
    func(std::forward<Args>(args)...);
    auto stop = std::chrono::high_resolution_clock::now();
    return stop - start;
}

class TestObject : public GCObject {
public:
    TestObject(int id)
        : id(id) {
        registry.insert(this);
    }

    ~TestObject() {
        registry.erase(this);
    }

    void addChild(GCObject *obj) {
        children.insert(obj);
    }

    void removeChild(GCObject *obj) {
        children.erase(obj);
    }

    int getID() {
        return id;
    }

    static std::unordered_set<TestObject *> const &getRegistry() {
        return registry;
    }

    virtual void traverseAndMarkImpl() override {
        for (GCObject *child : children) {
            child->traverseAndMark();
        }
    }

private:
    int id;
    std::unordered_set<GCObject *> children;

    static inline std::unordered_set<TestObject *> registry;
};

#include <iostream>

int main() {
    GCManager gcm;

    auto A = gcm.alloc<TestObject>(1);
    auto B = gcm.alloc<TestObject>(2);
    auto C = gcm.alloc<TestObject>(3);

    A->addChild(B);
    B->addChild(C);
    C->addChild(B);

    gcm.addRoot(A);
    gcm.addRoot(C);

    std::cout << "-- 1st GC --" << std::endl;
    gcm.collect();
    std::cout << "Total objects: " << TestObject::getRegistry().size() << std::endl;
    for (auto obj : TestObject::getRegistry()) {
        std::cout << "Object ID: " << obj->getID() << std::endl;
    }

    gcm.removeRoot(A);

    std::cout << "-- 2nd GC --" << std::endl;
    gcm.collect();
    std::cout << "Total objects: " << TestObject::getRegistry().size() << std::endl;
    for (auto obj : TestObject::getRegistry()) {
        std::cout << "Object ID: " << obj->getID() << std::endl;
    }

    gcm.removeRoot(C);

    std::cout << "-- 3rd GC --" << std::endl;
    gcm.collect();
    std::cout << "Total objects: " << TestObject::getRegistry().size() << std::endl;
    for (auto obj : TestObject::getRegistry()) {
        std::cout << "Object ID: " << obj->getID() << std::endl;
    }
}
