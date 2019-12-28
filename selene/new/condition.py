# MIT License
#
# Copyright (c) 2015-2019 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import List, Any

from selene.common import predicate
from selene.driver import SeleneDriver
from selene.elements import SeleneCollection, SeleneElement
from selene.wait import Condition

# todo: consider the following type aliases
# ElementCondition = Condition[SeleneElement]
# CollectionCondition = Condition[SeleneCollection]
# BrowserCondition = Condition[SeleneDriver]


element_is_visible: Condition[SeleneElement] = \
    Condition.raise_if_not('is visible', lambda element: element().is_displayed())

element_is_hidden: Condition[SeleneElement] = Condition.as_not(element_is_visible, 'is hidden')

element_is_enabled: Condition[SeleneElement] = \
    Condition.raise_if_not('is enabled', lambda element: element().is_enabled())

element_is_disabled: Condition[SeleneElement] = Condition.as_not(element_is_enabled)

element_is_present: Condition[SeleneElement] = \
    Condition.raise_if_not('is visible', lambda element: element() is not None)

element_is_absent: Condition[SeleneElement] = Condition.as_not(element_is_present)

element_is_focused: Condition[SeleneElement] = Condition.raise_if_not(
    'is focused',
    # todo: change in the following line to element.execute_script or element.config.driver.execute_script
    lambda element: element() == element._webdriver.execute_script('return document.activeElement')
)


def element_has_text(expected: str,
                     describing_matched_to='has text',
                     compared_by_predicate_to=predicate.includes) -> Condition[SeleneElement]:
    def text(element: SeleneElement) -> str:
        return element().text

    return Condition.raise_if_not_actual(describing_matched_to + ' ' + expected,
                                         text,
                                         compared_by_predicate_to(expected))


def element_has_exact_text(expected: str) -> Condition[SeleneElement]:
    return element_has_text(expected, 'has exact text', predicate.equals)


def element_has_attribute(name: str):
    def attribute_value(element: SeleneElement) -> str:
        return element().get_attribute(name)

    def attribute_values(collection: SeleneCollection) -> List[str]:
        return [element.get_attribute(name) for element in collection()]

    raw_attribute_condition = Condition.raise_if_not_actual('has attribute ' + name,
                                                            attribute_value,
                                                            predicate.is_truthy)

    class ConditionWithValues(Condition[SeleneElement]):

        def value(self, expected: str) -> Condition[SeleneElement]:
            return Condition.raise_if_not_actual(f"has attribute '{name}' with value '{expected}'",
                                                 attribute_value,
                                                 predicate.equals(expected))

        def value_containing(self, expected: str) -> Condition[SeleneElement]:
            return Condition.raise_if_not_actual(f"has attribute '{name}' with value containing '{expected}'",
                                                 attribute_value,
                                                 predicate.includes(expected))

        def values(self, *expected: List[str]) -> Condition[SeleneCollection]:
            return Condition.raise_if_not_actual(f"has attribute '{name}' with values '{expected}'",
                                                 attribute_values,
                                                 predicate.equals_to_list(expected))

        def values_containing(self, *expected: List[str]) -> Condition[SeleneCollection]:
            return Condition.raise_if_not_actual(f"has attribute '{name}' with values containing '{expected}'",
                                                 attribute_values,
                                                 predicate.equals_by_contains_to_list(expected))

    return ConditionWithValues(str(raw_attribute_condition), raw_attribute_condition.call)


element_is_selected: Condition[SeleneElement] = element_has_attribute('elementIsSelected')


def element_has_value(expected: str) -> Condition[SeleneElement]:
    return element_has_attribute('value').value(expected)


def element_has_value_containing(expected: str) -> Condition[SeleneElement]:
    return element_has_attribute('value').value_containing(expected)


def element_has_css_class(expected: str) -> Condition[SeleneElement]:
    def class_attribute_value(element: SeleneElement) -> str:
        return element().get_attribute('class')

    return Condition.raise_if_not_actual(f"has css class '{expected}'",
                                         class_attribute_value,
                                         predicate.includes_word(expected))


element_is_blank = element_has_exact_text('').and_(element_has_value(''))


def collection_has_size(expected: int,
                        describing_matched_to='has size',
                        compared_by_predicate_to=predicate.equals) -> Condition[SeleneCollection]:
    def size(collection: SeleneCollection) -> int:
        return len(collection())

    return Condition.raise_if_not_actual(f'{describing_matched_to} {expected}',
                                         size,
                                         compared_by_predicate_to(expected))


def collection_has_size_greater_than(expected: int) -> Condition[SeleneCollection]:
    return collection_has_size(expected, 'has size greater than', predicate.is_greater_than)


def collection_has_size_greater_than_or_equal(expected: int) -> Condition[SeleneCollection]:
    return collection_has_size(expected, 'has size greater than or equal', predicate.is_greater_than_or_equal)


def collection_has_size_less_than(expected: int) -> Condition[SeleneCollection]:
    return collection_has_size(expected, 'has size less than', predicate.is_less_than)


def collection_has_size_less_than_or_equal(expected: int) -> Condition[SeleneCollection]:
    return collection_has_size(expected, 'has size less than or equal', predicate.is_less_than_or_equal)


def collection_has_texts(self, *expected: List[str]) -> Condition[SeleneCollection]:
    def visible_texts(collection: SeleneCollection) -> List[str]:
        return [webelement.text for webelement in collection() if webelement.is_displayed()]

    return Condition.raise_if_not_actual(f'has texts {expected}',
                                         visible_texts,
                                         predicate.equals_by_contains_to_list(expected))


def collection_has_exact_texts(self, *expected: List[str]) -> Condition[SeleneCollection]:
    def visible_texts(collection: SeleneCollection) -> List[str]:
        return [webelement.text for webelement in collection() if webelement.is_displayed()]

    return Condition.raise_if_not_actual(f'has exact texts {expected}',
                                         visible_texts,
                                         predicate.equals_to_list(expected))


# todo: consider refactoring the code like below by moving outside fns like url, title, etc...
# todo: probably we will do that nevertheless when reusing "commands&queries" inside element class definitions
def browser_has_url(expected: str,
                    describing_matched_to='has url',
                    compared_by_predicate_to=predicate.equals) -> Condition[SeleneDriver]:
    def url(browser: SeleneDriver) -> str:
        return browser().current_url

    return Condition.raise_if_not_actual(f'{describing_matched_to} + {expected}',
                                         url,
                                         compared_by_predicate_to(expected))


def browser_has_url_containing(expected: str) -> Condition[SeleneDriver]:
    return browser_has_url(expected, 'has url containing', predicate.includes)


def browser_has_title(expected: str,
                      describing_matched_to='has title',
                      compared_by_predicate_to=predicate.equals) -> Condition[SeleneDriver]:
    def title(browser: SeleneDriver) -> str:
        return browser().title

    return Condition.raise_if_not_actual(f'{describing_matched_to} + {expected}',
                                         title,
                                         compared_by_predicate_to(expected))


def browser_has_title_containing(expected: str) -> Condition[SeleneDriver]:
    return browser_has_title(expected, 'has title containing', predicate.includes)


def browser_has_tabs_number(expected: int,
                            describing_matched_to='has tabs number',
                            compared_by_predicate_to=predicate.equals) -> Condition[SeleneDriver]:
    def tabs_number(browser: SeleneDriver) -> int:
        return len(browser().window_handles)

    return Condition.raise_if_not_actual(f'{describing_matched_to} {expected}',
                                         tabs_number,
                                         compared_by_predicate_to(expected))


def browser_has_tabs_number_greater_than(expected: int) -> Condition[SeleneDriver]:
    return browser_has_tabs_number(expected, 'has tabs number greater than', predicate.is_greater_than)


def browser_has_tabs_number_greater_than_or_equal(expected: int) -> Condition[SeleneDriver]:
    return browser_has_tabs_number(expected, 'has tabs number greater than or equal',
                                   predicate.is_greater_than_or_equal)


def browser_has_tabs_number_less_than(expected: int) -> Condition[SeleneDriver]:
    return browser_has_tabs_number(expected, 'has tabs number less than', predicate.is_less_than)


def browser_has_tabs_number_less_than_or_equal(expected: int) -> Condition[SeleneDriver]:
    return browser_has_tabs_number(expected, 'has tabs number less than or equal', predicate.is_less_than_or_equal)


def browser_has_js_returned(expected: Any,
                            script: str,
                            *args) -> Condition[SeleneDriver]:
    def script_result(browser: SeleneDriver):
        return browser().execute_script(script, *args)

    return Condition.raise_if_not_actual(f'has the ```{script}``` script returned {expected}',
                                         script_result,
                                         predicate.equals(expected))